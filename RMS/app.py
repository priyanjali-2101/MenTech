import streamlit as st
import requests

BASE_URL = "http://127.0.0.1:8000"

# ✅ Page Config
st.set_page_config(
    page_title="Risk Management System",
    page_icon="🛡️",
    layout="wide"
)

# ✅ Session State — Token store karne ke liye
if "token" not in st.session_state:
    st.session_state.token = None
if "user_name" not in st.session_state:
    st.session_state.user_name = None
if "user_role" not in st.session_state:
    st.session_state.user_role = None


# ✅ Helper Function — API calls ke liye
def api_call(method, endpoint, data=None, params=None):
    url = f"{BASE_URL}{endpoint}"
    headers = {}

    if st.session_state.token:
        headers["Authorization"] = f"Bearer {st.session_state.token}"

    try:
        if method == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)

        return response.json()
    except Exception as e:
        return {"error": str(e)}


# ✅ Login Page
def login_page():
    st.title("🛡️ Risk Management System")
    st.subheader("Login")

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        email    = st.text_input("Email")
        password = st.text_input("Password", type="password")

        col_a, col_b = st.columns(2)

        with col_a:
            if st.button("Login", use_container_width=True):
                if email and password:
                    result = api_call("POST", "/users/login", {
                        "email"   : email,
                        "password": password
                    })
                    if "access_token" in result:
                        st.session_state.token     = result["access_token"]
                        st.session_state.user_name = result["name"]
                        st.session_state.user_role = result["role"]
                        st.success(f"Welcome {result['name']}!")
                        st.rerun()
                    else:
                        st.error("Invalid email or password!")
                else:
                    st.warning("Please fill all fields!")

        with col_b:
            if st.button("Register", use_container_width=True):
                st.session_state.page = "register"
                st.rerun()


# ✅ Register Page
def register_page():
    st.title("🛡️ Risk Management System")
    st.subheader("Register")

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        name     = st.text_input("Full Name")
        email    = st.text_input("Email")
        password = st.text_input("Password", type="password")
        role     = st.selectbox("Role", ["Employee", "Manager", "Admin"])

        col_a, col_b = st.columns(2)

        with col_a:
            if st.button("Register", use_container_width=True):
                if name and email and password:
                    result = api_call("POST", "/users/register", {
                        "name"    : name,
                        "email"   : email,
                        "password": password,
                        "role"    : role
                    })
                    if "id" in result:
                        st.success("Registered successfully! Please login.")
                        st.session_state.page = "login"
                        st.rerun()
                    else:
                        st.error(result.get("detail", "Registration failed!"))
                else:
                    st.warning("Please fill all fields!")

        with col_b:
            if st.button("Back to Login", use_container_width=True):
                st.session_state.page = "login"
                st.rerun()


# ✅ Dashboard Page
def dashboard_page():
    st.title("📊 Dashboard")

    result = api_call("GET", "/risks/dashboard")

    if "total_risks" in result:
        col1, col2, col3 = st.columns(3)
        col4, col5, col6 = st.columns(3)

        with col1:
            st.metric("Total Risks", result["total_risks"])
        with col2:
            st.metric("Open Risks", result["open_risks"])
        with col3:
            st.metric("In Progress", result["in_progress"])
        with col4:
            st.metric("Resolved", result["resolved_risks"])
        with col5:
            st.metric("Closed", result["closed_risks"])
        with col6:
            st.metric("Critical", result["critical_risks"])

    st.divider()

    # Recent Risks
    st.subheader("📋 Recent Risks")
    risks = api_call("GET", "/risks/")

    if isinstance(risks, list) and risks:
        for risk in risks:
            with st.expander(f"#{risk['id']} — {risk['title']}"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**Priority:** {risk['priority']}")
                with col2:
                    st.write(f"**Status:** {risk['status']}")
                with col3:
                    st.write(f"**Category:** {risk.get('category', 'N/A')}")
                st.write(f"**Due Date:** {risk.get('due_date', 'N/A')}")
                st.write(f"**Mitigation:** {risk.get('mitigation', 'N/A')}")
    else:
        st.info("No risks found!")


# ✅ Risks Page
def risks_page():
    st.title("⚠️ Risks Management")

    tab1, tab2, tab3 = st.tabs(["View Risks", "Create Risk", "Search & Filter"])

    # Tab 1 — View Risks
    with tab1:
        st.subheader("All Risks")

        risks = api_call("GET", "/risks/")

        if isinstance(risks, list) and risks:
            for risk in risks:

                # Priority color
                color = {
                    "Critical": "🔴",
                    "High"    : "🟠",
                    "Medium"  : "🟡",
                    "Low"     : "🟢"
                }.get(risk["priority"], "⚪")

                with st.expander(f"{color} #{risk['id']} — {risk['title']} | {risk['status']}"):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.write(f"**Priority:** {risk['priority']}")
                        st.write(f"**Status:** {risk['status']}")
                        st.write(f"**Category:** {risk.get('category', 'N/A')}")

                    with col2:
                        st.write(f"**Due Date:** {risk.get('due_date', 'N/A')}")
                        st.write(f"**Assigned To:** {risk.get('assigned_to', 'Unassigned')}")
                        st.write(f"**Created By:** {risk.get('created_by', 'N/A')}")

                    st.write(f"**Description:** {risk.get('description', 'N/A')}")
                    st.write(f"**Mitigation:** {risk.get('mitigation', 'N/A')}")

                    # Update Status
                    st.divider()
                    col_a, col_b, col_c = st.columns(3)

                    with col_a:
                        # new_status = st.selectbox(
                        #     "Update Status",
                        #     ["Open", "Assigned", "In Progress", "Resolved", "Closed"],
                        #     key=f"status_{risk['id']}"
                        # )
                        status_options = ["Open", "Assigned", "In Progress", "Resolved", "Closed"]
                        new_status = st.selectbox(
                            "Update Status",
                            status_options,
                            index=status_options.index(risk['status']) if risk['status'] in status_options else 0,
                            key=f"status_{risk['id']}"
                        )

                    with col_b:
                        if st.button("Update", key=f"update_{risk['id']}"):
                            result = api_call("PUT", f"/risks/{risk['id']}", {
                                "status": new_status
                            })
                            if "id" in result:
                                st.success("Status updated!")
                                st.rerun()

                    with col_c:
                        if st.session_state.user_role == "Admin":
                            if st.button("🗑️ Delete", key=f"delete_{risk['id']}"):
                                result = api_call("DELETE", f"/risks/{risk['id']}")
                                st.success("Risk deleted!")
                                st.rerun()
        else:
            st.info("No risks found!")

    # Tab 2 — Create Risk
    with tab2:
        st.subheader("Create New Risk")

        title       = st.text_input("Risk Title")
        description = st.text_area("Description")
        priority    = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"])
        category    = st.selectbox("Category", [
            "Security", "Infrastructure", "Bug", "Performance", "Maintenance", "Data Privacy"
        ])
        due_date    = st.date_input("Due Date")
        mitigation  = st.text_area("Mitigation Plan")

        if st.button("Create Risk", use_container_width=True):
            if title and description:
                result = api_call("POST", "/risks/", {
                    "title"      : title,
                    "description": description,
                    "priority"   : priority,
                    "category"   : category,
                    "due_date"   : str(due_date),
                    "mitigation" : mitigation
                })
                if "id" in result:
                    st.success(f"Risk created successfully! ID: {result['id']}")
                else:
                    st.error("Failed to create risk!")
            else:
                st.warning("Please fill Title and Description!")

    # Tab 3 — Search & Filter
    with tab3:
        st.subheader("Search & Filter Risks")

        col1, col2, col3 = st.columns(3)

        with col1:
            search   = st.text_input("Search by keyword")
        with col2:
            f_status = st.selectbox("Filter by Status", ["All", "Open", "Assigned", "In Progress", "Resolved", "Closed"])
        with col3:
            f_priority = st.selectbox("Filter by Priority", ["All", "Low", "Medium", "High", "Critical"])

        params = {}
        if search:
            params["search"] = search
        if f_status != "All":
            params["status"] = f_status
        if f_priority != "All":
            params["priority"] = f_priority

        if st.button("Search", use_container_width=True):
            results = api_call("GET", "/risks/", params=params)

            if isinstance(results, list) and results:
                st.success(f"Found {len(results)} risks!")
                for risk in results:
                    st.write(f"**#{risk['id']}** — {risk['title']} | {risk['priority']} | {risk['status']}")
            else:
                st.info("No risks found!")


# ✅ AI Features Page
def ai_page():
    st.title("🤖 AI Features")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Analyze Risk",
        "Mitigation Plan",
        "AI Chat",
        "Risk Summary",
        "Auto Workflow"
    ])

    # Tab 1 — Analyze
    with tab1:
        st.subheader("🔍 AI Risk Analyzer")
        title       = st.text_input("Risk Title")
        description = st.text_area("Risk Description")

        if st.button("Analyze", use_container_width=True):
            if title and description:
                with st.spinner("AI analyzing risk..."):
                    result = api_call("POST", "/ai/analyze", {
                        "title"      : title,
                        "description": description
                    })
                if "analysis" in result:
                    analysis = result["analysis"]
                    st.success("Analysis Complete!")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Priority", analysis.get("priority"))
                        st.metric("Category", analysis.get("category"))
                    with col2:
                        st.write(f"**Mitigation:** {analysis.get('mitigation')}")
                        st.write(f"**Reason:** {analysis.get('reason')}")
            else:
                st.warning("Please fill all fields!")

    # Tab 2 — Mitigation
    with tab2:
        st.subheader("🛡️ Mitigation Plan Generator")
        title       = st.text_input("Risk Title", key="mit_title")
        description = st.text_area("Description", key="mit_desc")
        priority    = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"])

        if st.button("Generate Plan", use_container_width=True):
            if title and description:
                with st.spinner("AI generating mitigation plan..."):
                    result = api_call("POST", "/ai/mitigation", {
                        "title"      : title,
                        "description": description,
                        "priority"   : priority
                    })
                if "mitigation_plan" in result:
                    st.success("Mitigation Plan Ready!")
                    st.markdown(result["mitigation_plan"])
            else:
                st.warning("Please fill all fields!")

    # Tab 3 — Chat
    with tab3:
        st.subheader("💬 AI Chat Assistant")

        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Show messages
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        # Chat input
        question = st.chat_input("Ask about risks...")

        if question:
            st.session_state.messages.append({
                "role"   : "user",
                "content": question
            })

            with st.spinner("AI thinking..."):
                result = api_call("POST", "/ai/chat", {
                    "question": question
                })

            answer = result.get("answer", "Sorry, could not get answer!")

            st.session_state.messages.append({
                "role"   : "assistant",
                "content": answer
            })
            st.rerun()

    # Tab 4 — Summary
    with tab4:
        st.subheader("📋 AI Risk Summary")

        if st.button("Generate Summary", use_container_width=True):
            with st.spinner("AI generating summary..."):
                result = api_call("GET", "/ai/summary")
            if "summary" in result:
                st.success("Summary Ready!")
                st.markdown(result["summary"])

    # Tab 5 — Workflow
    with tab5:
        st.subheader("⚡ Auto Workflow")
        st.info("AI will automatically analyze and assign the risk!")

        risk_id     = st.number_input("Risk ID", min_value=1, step=1)
        title       = st.text_input("Risk Title", key="wf_title")
        description = st.text_area("Description", key="wf_desc")

        if st.button("Run Workflow", use_container_width=True):
            if title and description:
                with st.spinner("AI running workflow..."):
                    result = api_call("POST", "/ai/workflow", {
                        "risk_id"    : risk_id,
                        "title"      : title,
                        "description": description
                    })
                if "message" in result:
                    st.success(result["message"])
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Priority", result.get("priority"))
                        st.metric("Status", result.get("status"))
                    with col2:
                        st.metric("Assigned To", result.get("assigned_to"))
                        st.write(f"**Mitigation:** {result.get('mitigation')}")
            else:
                st.warning("Please fill all fields!")


# ✅ Users Page
def users_page():
    st.title("👥 Users Management")

    result = api_call("GET", "/users/")

    if isinstance(result, list):
        for user in result:
            with st.expander(f"#{user['id']} — {user['name']} ({user['role']})"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Email:** {user['email']}")
                with col2:
                    st.write(f"**Role:** {user['role']}")
                    st.write(f"**Active:** {user['is_active']}")
    else:
        st.error("Could not load users!")


# ✅ Comments Page
def comments_page():
    st.title("💬 Comments")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Add Comment")
        risk_id = st.number_input("Risk ID", min_value=1, step=1)
        content = st.text_area("Comment")

        if st.button("Add Comment", use_container_width=True):
            if content:
                result = api_call("POST", "/comments/", {
                    "content": content,
                    "risk_id": risk_id
                })
                if "id" in result:
                    st.success("Comment added!")
                else:
                    st.error("Failed to add comment!")

    with col2:
        st.subheader("View Comments")
        view_risk_id = st.number_input("Risk ID to view", min_value=1, step=1, key="view_id")

        if st.button("Get Comments", use_container_width=True):
            result = api_call("GET", f"/comments/{view_risk_id}")

            if isinstance(result, list) and result:
                for comment in result:
                    st.write(f"💬 {comment['content']}")
                    st.caption(f"User ID: {comment['user_id']}")
                    st.divider()
            else:
                st.info("No comments found!")


# ✅ Sidebar + Navigation
def main():
    if not st.session_state.token:
        if "page" not in st.session_state:
            st.session_state.page = "login"

        if st.session_state.page == "login":
            login_page()
        else:
            register_page()
    else:
        # Sidebar
        with st.sidebar:
            st.title("🛡️ RMS")
            st.write(f"👤 **{st.session_state.user_name}**")
            st.write(f"🎭 **{st.session_state.user_role}**")
            st.divider()

            page = st.radio("Navigation", [
                "📊 Dashboard",
                "⚠️ Risks",
                "🤖 AI Features",
                "👥 Users",
                "💬 Comments"
            ])

            st.divider()
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.token     = None
                st.session_state.user_name = None
                st.session_state.user_role = None
                st.rerun()

        # Pages
        if page == "📊 Dashboard":
            dashboard_page()
        elif page == "⚠️ Risks":
            risks_page()
        elif page == "🤖 AI Features":
            ai_page()
        elif page == "👥 Users":
            users_page()
        elif page == "💬 Comments":
            comments_page()


if __name__ == "__main__":
    main()


    #streamlit run app.py