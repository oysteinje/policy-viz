
import streamlit as st
import json
from azure.identity import DefaultAzureCredential
from azure.mgmt.subscription import SubscriptionClient
from azure.mgmt.resource import PolicyClient
from azure.mgmt.managementgroups import ManagementGroupsAPI

def initialize_azure():
    """Initialize Azure credentials and clients"""
    try:
        credential = DefaultAzureCredential()
        subscription_client = SubscriptionClient(credential)
        management_group_client = ManagementGroupsAPI(credential)
        return credential, subscription_client, management_group_client
    except Exception as e:
        st.error(f"Failed to authenticate with Azure: {str(e)}")
        st.info("Please ensure you're logged in using 'az login'")
        return None, None, None

def get_subscriptions(subscription_client):
    """Get list of subscriptions"""
    try:
        return list(subscription_client.subscriptions.list())
    except Exception as e:
        st.error(f"Failed to fetch subscriptions: {str(e)}")
        return []

def get_policy_assignments(credential, subscription_id):
    """Get policy assignments for a subscription"""
    try:
        policy_client = PolicyClient(credential, subscription_id)
        return list(policy_client.policy_assignments.list())
    except Exception as e:
        st.error(f"Failed to fetch policy assignments: {str(e)}")
        return []

def get_management_groups(management_group_client):
    """Get management group structure"""
    try:
        return list(management_group_client.management_groups.list())
    except Exception as e:
        st.error(f"Failed to fetch management groups: {str(e)}")
        return []

def is_subscription_in_notscope(subscription_id, not_scopes, management_groups):
    """Check if the subscription is within any of the notScopes"""
    for not_scope in not_scopes:
        if subscription_id in not_scope:
            return True
        for mg in management_groups:
            if mg.id in not_scope:
                return True
    return False

def display_parameters(parameters):
    """Display parameters in a formatted way"""
    if not parameters:
        st.info("No parameters set for this policy assignment")
        return

    st.write("Parameters:")
    for param_name, param_value in parameters.items():
        with st.container():
            st.markdown(f"**{param_name}:**")
            value = param_value.value if hasattr(param_value, 'value') else param_value
            try:
                if isinstance(value, (dict, list)):
                    st.json(value)
                else:
                    st.write(value)
            except:
                st.write(str(value))
            st.markdown("---")

def main():
    st.title("Azure Policy Explorer")
    st.write("Explore Azure Policies across your subscriptions")

    with st.spinner("Connecting to Azure..."):
        credential, subscription_client, management_group_client = initialize_azure()

    if credential and subscription_client and management_group_client:
        subscriptions = get_subscriptions(subscription_client)
        management_groups = get_management_groups(management_group_client)

        if subscriptions:
            sub_options = {f"{sub.display_name} ({sub.subscription_id})": sub for sub in subscriptions}
            selected_sub = st.selectbox("Select Subscription", options=list(sub_options.keys()))

            if selected_sub:
                subscription = sub_options[selected_sub]
                st.write(f"Selected: {subscription.display_name}")

                with st.expander("Subscription Details"):
                    st.write(f"Subscription ID: {subscription.subscription_id}")
                    st.write(f"State: {subscription.state}")
                    if hasattr(subscription, 'tenant_id'):
                        st.write(f"Tenant ID: {subscription.tenant_id}")

                st.subheader("Policy Assignments")
                with st.spinner("Fetching policy assignments..."):
                    policies = get_policy_assignments(credential, subscription.subscription_id)

                if policies:
                    for policy in policies:
                        if policy.not_scopes and is_subscription_in_notscope(subscription.subscription_id, policy.not_scopes, management_groups):
                            continue  # Skip this policy if the subscription is in the notScopes

                        with st.expander(f"📋 {policy.display_name or policy.name}"):
                            st.write(f"Name: {policy.name}")
                            if policy.description:
                                st.write(f"Description: {policy.description}")
                            if policy.scope:
                                st.write(f"Scope: {policy.scope}")
                            if policy.not_scopes:
                                st.write("Not Scopes:")
                                st.json(policy.not_scopes)

                            st.markdown("---")
                            if hasattr(policy, 'parameters'):
                                display_parameters(policy.parameters)
                            else:
                                st.info("No parameters available for this policy assignment")
                else:
                    st.info("No policy assignments found for this subscription")

if __name__ == "__main__":
    main()
