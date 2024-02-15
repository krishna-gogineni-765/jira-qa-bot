import streamlit as st

from src.brain.orchestrator import Orchestrator
from src.ipaas.jira_integration import JiraIntegration
from src.ipaas.integration_store import IntegrationStore

integration_store = IntegrationStore()

def render_jira_config_page():
    st.title('Configure JIRA Integration')

    with st.form(key='jira_config_form'):
        jira_url = st.text_input('JIRA URL', help='The base URL for your JIRA instance')
        jira_user = st.text_input('JIRA Username', help='Your JIRA username')
        jira_api_token = st.text_input('JIRA API Token', type='password', help='Your JIRA API token')
        submit_button = st.form_submit_button(label='Save Configuration')
        if submit_button:
            st.success('Configuration saved successfully!')
            integration_store.add_integration(jira_url, JiraIntegration(jira_url))

def render_jira_entities_page():
    st.title('View JIRA Entities')
    if len(integration_store.get_all_integrations()) == 0:
        st.write('No JIRA integrations configured yet. Please configure one first.')
        return

    integration_url = st.selectbox('Select JIRA Integration', list(integration_store.get_all_integrations()))

    entities = integration_store.get_integration(integration_url).get_projects()
    st.write('JIRA Projects in your organization:')
    st.write(entities)


def render_jira_dashboard_query_page():
    st.title('Query JIRA Dashboards')
    if len(integration_store.get_all_integrations()) == 0:
        st.write('No JIRA integrations configured yet. Please configure one first.')
        return

    with st.form(key='jira_query_form'):
        integration_url = st.selectbox('Select JIRA Integration', list(integration_store.get_all_integrations()))
        question = st.text_input('Ask a question about your JIRA data')
        submit_button = st.form_submit_button(label='Submit')

        if submit_button:
            try:
                orchestrator = Orchestrator()
                answer = orchestrator.run_query(question)
                st.write('Answer: ', answer)
            except Exception as e:
                st.error(f'Error: {e}')

def main():
    st.sidebar.title('Navigation')
    page = st.sidebar.radio('Select a page:',
                             ['Configure Integration',
                              'View Entities',
                              'Query Dashboards'])

    if page == 'Configure Integration':
        render_jira_config_page()
    elif page == 'View Entities':
        render_jira_entities_page()
    elif page == 'Query Dashboards':
        render_jira_dashboard_query_page()

if __name__ == "__main__":
    main()
