import streamlit as st

from loaders.cv_loader import (
    load_cv,
    documents_to_text,
)

from chains.cv_chain import analyze_cv
from chains.matching_chain import match_candidate_to_program

from services.program_service import find_programs
from services.professor_service import find_professors

from agents.chat_agent import get_chat_agent
from services import storage

storage.init_db()


st.set_page_config(
    page_title="MasterFinder AI",
    page_icon="🎓",
    layout="wide",
)


# =====================================================
# Helpers
# =====================================================

def program_key(program) -> str:
    return f"{program.university}::{program.program_name}"


def professor_key(professor) -> str:
    return f"{professor.university}::{professor.name}"


# =====================================================
# Session state — loaded once from SQLite so favorites,
# CV, last search results, and chat survive a refresh
# or app restart.
# =====================================================

if "db_loaded" not in st.session_state:
    st.session_state.candidate = storage.load_candidate()
    st.session_state.programs = storage.load_programs()
    st.session_state.professors = storage.load_professors()
    st.session_state.favorite_programs = storage.load_favorite_programs()
    st.session_state.favorite_professors = storage.load_favorite_professors()
    st.session_state.messages = storage.load_messages()
    st.session_state.matches = {}
    st.session_state.db_loaded = True

if "chat_agent" not in st.session_state:
    st.session_state.chat_agent = get_chat_agent()

CHAT_CONFIG = {
    "configurable": {
        "thread_id": "streamlit-user-session"
    }
}


# =====================================================
# Header
# =====================================================

st.title("🎓 MasterFinder AI")

st.caption(
    "AI-powered Master's program and academic researcher finder"
)


# =====================================================
# Sidebar — search preferences (form OR CV)
# =====================================================

with st.sidebar:

    st.header("🔍 Search Preferences")

    search_mode = st.radio(
        "Define your field of interest via",
        [
            "📝 Manual form",
            "📄 My CV",
        ],
    )

    derived_field_default = ""

    if search_mode == "📄 My CV":

        st.caption(
            "Upload your CV once — MasterFinder will use it "
            "to figure out your field automatically."
        )

        uploaded_cv = st.file_uploader(
            "Upload your CV (PDF)",
            type=["pdf"],
            key="sidebar_cv_uploader",
        )

        if uploaded_cv and st.button(
            "Analyze CV",
            use_container_width=True,
        ):

            with st.spinner(
                "Reading and analyzing your CV..."
            ):
                try:
                    documents = load_cv(uploaded_cv)
                    cv_text = documents_to_text(documents)
                    candidate = analyze_cv(cv_text)

                    st.session_state.candidate = candidate
                    st.session_state.matches = {}
                    storage.save_candidate(candidate)

                except Exception as e:
                    st.error(f"CV analysis failed: {e}")

        if st.session_state.candidate:

            st.success("CV analyzed ✅")

            with st.expander("View extracted profile"):
                st.write(
                    f"**Name:** "
                    f"{st.session_state.candidate.name or 'Not found'}"
                )
                if st.session_state.candidate.skills:
                    st.write("**Skills:** " + ", ".join(
                        st.session_state.candidate.skills
                    ))
                if st.session_state.candidate.research_interests:
                    st.write("**Research interests:** " + ", ".join(
                        st.session_state.candidate.research_interests
                    ))

            interests = (
                st.session_state.candidate.research_interests
                or st.session_state.candidate.skills
            )
            derived_field_default = ", ".join(interests[:8])

        else:
            st.info(
                "Upload and analyze your CV to continue."
            )

        field = st.text_area(
            "Field / interests (auto-filled from CV, editable)",
            value=derived_field_default,
            height=80,
        )

    else:

        field = st.text_input(
            "Field",
            value="Artificial Intelligence",
        )

    st.divider()

    countries = st.multiselect(
        "Countries",
        [
            "Germany",
            "Norway",
            "Canada",
            "Netherlands",
            "Sweden",
            "Finland",
            "Denmark",
            "Austria",
        ],
    )

    degree = st.selectbox(
        "Degree",
        [
            "Master's",
            "MSc",
            "MEng",
            "Other",
        ],
    )

    language = st.selectbox(
        "Preferred language",
        [
            "English",
            "German",
            "Norwegian",
            "Any",
        ],
    )

    max_tuition = st.text_input(
        "Maximum tuition",
        value="No strict limit",
    )

    search_button = st.button(
        "🔍 Search Programs",
        use_container_width=True,
        type="primary",
    )

    with st.expander("⚙️ Data & Storage"):
        st.caption(
            "Your CV, favorites, last search results, and chat "
            "are saved locally in a SQLite database and survive "
            "a page refresh or app restart."
        )
        if st.button(
            "🗑️ Clear all saved data",
            use_container_width=True,
        ):
            storage.clear_all()
            st.session_state.clear()
            st.rerun()


# =====================================================
# Tabs
# =====================================================

program_tab, professor_tab, favorites_tab, profile_tab, chat_tab = st.tabs(
    [
        "🎓 Programs",
        "👨‍🏫 Professors",
        "⭐ Favorites",
        "🙍 My Profile",
        "💬 AI Advisor",
    ]
)


# =====================================================
# Program search & display
# =====================================================

def render_program_card(program, index, key_prefix):

    fav_key = program_key(program)
    is_favorite = fav_key in st.session_state.favorite_programs

    with st.container(border=True):

        header_col, fav_col = st.columns([6, 1])

        with header_col:
            st.subheader(program.program_name)
            st.caption(f"{program.university} · {program.country}")

        with fav_col:
            star_label = "★" if is_favorite else "☆"
            if st.button(
                star_label,
                key=f"{key_prefix}_fav_{index}",
                help="Toggle favorite",
            ):
                if is_favorite:
                    del st.session_state.favorite_programs[fav_key]
                    storage.remove_favorite_program(fav_key)
                else:
                    st.session_state.favorite_programs[fav_key] = program
                    storage.add_favorite_program(fav_key, program)
                st.rerun()

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Tuition", program.tuition or "Not found")

        with col2:
            st.metric("ECTS", program.ects or "Not found")

        with col3:
            st.metric("Deadline", program.deadline or "Not found")

        col4, col5 = st.columns(2)

        with col4:
            st.write(f"**Duration:** {program.duration or 'Not found'}")

        with col5:
            st.write(f"**Language:** {program.language or 'Not found'}")

        if program.admission_requirements:
            with st.expander("Admission requirements"):
                for requirement in program.admission_requirements:
                    st.write(f"- {requirement}")

        if program.official_program_url:
            st.link_button(
                "🔗 Official Program Website",
                program.official_program_url,
            )

        col_a, col_b = st.columns(2)

        with col_a:
            if st.button(
                "👨‍🏫 Find Researchers Here",
                key=f"{key_prefix}_find_prof_{index}",
                use_container_width=True,
            ):
                with st.spinner(
                    f"Researching professors at {program.university}..."
                ):
                    try:
                        result = find_professors(
                            program.university,
                            field,
                        )
                        st.session_state.professors = result.professors
                        storage.save_professors(result.professors)
                        st.success(
                            "Check the 👨‍🏫 Professors tab for results."
                        )
                    except Exception as e:
                        st.error(f"Professor research failed: {e}")

        with col_b:
            if st.session_state.candidate is not None:
                if st.button(
                    "🎯 Analyze My Fit",
                    key=f"{key_prefix}_match_{index}",
                    use_container_width=True,
                ):
                    with st.spinner("Analyzing fit..."):
                        try:
                            match = match_candidate_to_program(
                                st.session_state.candidate,
                                program,
                            )
                            st.session_state.matches[fav_key] = match
                        except Exception as e:
                            st.error(f"Matching failed: {e}")
            else:
                st.caption(
                    "Upload your CV in the sidebar to analyze fit."
                )

        if fav_key in st.session_state.matches:

            match = st.session_state.matches[fav_key]

            st.markdown("---")
            st.write(f"**Estimated fit: {match.score}/100**")
            st.progress(match.score / 100)

            if match.strengths:
                st.write("**Strengths:**")
                for s in match.strengths:
                    st.write(f"✓ {s}")

            if match.potential_gaps:
                st.write("**Potential gaps:**")
                for g in match.potential_gaps:
                    st.write(f"⚠️ {g}")

            st.caption(match.explanation)


with program_tab:

    st.subheader("Master's Programs")

    if search_button:

        if search_mode == "📄 My CV" and not st.session_state.candidate:
            st.warning(
                "Please upload and analyze your CV in the sidebar first."
            )

        elif not field.strip():
            st.warning(
                "Please provide a field of interest."
            )

        elif not countries:
            st.warning(
                "Please select at least one country."
            )

        else:

            with st.spinner(
                "Researching current university programs..."
            ):
                try:
                    result = find_programs(
                        countries,
                        field,
                        degree,
                        language,
                        max_tuition,
                    )

                    st.session_state.programs = result.programs
                    st.session_state.matches = {}
                    storage.save_programs(result.programs)

                    if st.session_state.programs:
                        st.success(
                            f"Found {len(st.session_state.programs)} program(s)."
                        )
                    else:
                        st.info(
                            "No verified programs were found for these filters."
                        )

                except Exception as e:
                    st.error(f"Research failed: {e}")

    if st.session_state.programs:
        for index, program in enumerate(st.session_state.programs):
            render_program_card(program, index, key_prefix="prog")
    else:
        st.info(
            "Set your preferences in the sidebar and click "
            "**🔍 Search Programs** to get started."
        )


# =====================================================
# Professor tab
# =====================================================

def render_professor_card(professor, index, key_prefix):

    fav_key = professor_key(professor)
    is_favorite = fav_key in st.session_state.favorite_professors

    with st.container(border=True):

        header_col, fav_col = st.columns([6, 1])

        with header_col:
            st.subheader(professor.name)
            st.caption(
                f"{professor.university} · "
                f"{professor.position or 'Position not found'}"
            )

        with fav_col:
            star_label = "★" if is_favorite else "☆"
            if st.button(
                star_label,
                key=f"{key_prefix}_fav_{index}",
                help="Toggle favorite",
            ):
                if is_favorite:
                    del st.session_state.favorite_professors[fav_key]
                    storage.remove_favorite_professor(fav_key)
                else:
                    st.session_state.favorite_professors[fav_key] = professor
                    storage.add_favorite_professor(fav_key, professor)
                st.rerun()

        if professor.research_areas:
            st.write(
                "**Research areas:** "
                + ", ".join(professor.research_areas)
            )

        st.write(
            f"**Official email:** "
            f"{professor.official_email or 'Not publicly listed'}"
        )

        if professor.relevance_reason:
            st.caption(professor.relevance_reason)

        if professor.official_profile_url:
            st.link_button(
                "🔗 Official Profile",
                professor.official_profile_url,
            )


with professor_tab:

    st.subheader("Top Relevant Professors / Researchers")

    if not st.session_state.professors:
        st.info(
            "Search for programs first, then click "
            "**👨‍🏫 Find Researchers Here** on a program card."
        )
    else:
        for index, professor in enumerate(st.session_state.professors):
            render_professor_card(professor, index, key_prefix="prof")


# =====================================================
# Favorites tab
# =====================================================

with favorites_tab:

    st.subheader("⭐ My Favorite Programs")

    if not st.session_state.favorite_programs:
        st.info(
            "No favorite programs yet. Click the ☆ button on any "
            "program card to save it here."
        )
    else:
        for index, program in enumerate(
            st.session_state.favorite_programs.values()
        ):
            render_program_card(program, index, key_prefix="fav_prog")

    st.divider()

    st.subheader("⭐ My Favorite Professors")

    if not st.session_state.favorite_professors:
        st.info(
            "No favorite professors yet. Click the ☆ button on any "
            "professor card to save it here."
        )
    else:
        for index, professor in enumerate(
            st.session_state.favorite_professors.values()
        ):
            render_professor_card(professor, index, key_prefix="fav_prof")


# =====================================================
# My Profile tab (CV summary — upload happens in the sidebar)
# =====================================================

with profile_tab:

    st.subheader("🙍 My Profile")

    if not st.session_state.candidate:
        st.info(
            "No CV analyzed yet. Choose **📄 My CV** in the sidebar "
            "search mode and upload your CV to build your profile."
        )
    else:
        candidate = st.session_state.candidate

        st.success("CV analyzed successfully.")

        col1, col2 = st.columns(2)

        with col1:
            st.write(f"**Name:** {candidate.name or 'Not found'}")
            st.write(f"**GPA:** {candidate.gpa or 'Not found'}")

        with col2:
            if candidate.languages:
                st.write("**Languages:** " + ", ".join(candidate.languages))

        if candidate.skills:
            with st.expander("Skills", expanded=True):
                for skill in candidate.skills:
                    st.write(f"- {skill}")

        if candidate.education:
            with st.expander("Education"):
                for education in candidate.education:
                    st.write(f"- {education}")

        if candidate.experience:
            with st.expander("Experience"):
                for experience in candidate.experience:
                    st.write(f"- {experience}")

        if candidate.projects:
            with st.expander("Projects"):
                for project in candidate.projects:
                    st.write(f"- {project}")

        if candidate.research_interests:
            with st.expander("Research Interests"):
                for interest in candidate.research_interests:
                    st.write(f"- {interest}")

        if candidate.certifications:
            with st.expander("Certifications"):
                for certification in candidate.certifications:
                    st.write(f"- {certification}")


# =====================================================
# Chat tab
# =====================================================

with chat_tab:

    st.subheader("💬 AI Study-Abroad Advisor")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_message = st.chat_input(
        "Ask about Master's programs..."
    )

    if user_message:

        st.session_state.messages.append(
            {
                "role": "user",
                "content": user_message,
            }
        )

        with st.chat_message("user"):
            st.markdown(user_message)

        with st.chat_message("assistant"):

            with st.spinner("Thinking..."):
                try:
                    result = st.session_state.chat_agent.invoke(
                        {
                            "messages": [
                                {
                                    "role": "user",
                                    "content": user_message,
                                }
                            ]
                        },
                        CHAT_CONFIG,
                    )

                    response = result["messages"][-1].content

                except Exception as e:
                    response = f"Research failed: {e}"

            st.markdown(response)

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": response,
            }
        )

        storage.save_messages(st.session_state.messages)
