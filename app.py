import streamlit as st
import json
from azure.identity import DefaultAzureCredential
from azure.mgmt.subscription import SubscriptionClient
from azure.mgmt.resource import PolicyClient

def initialize_azure():
    """Initialize Azure credentials and clients"""
    try:
        credential = DefaultAzureCredential()
        subscription_client = SubscriptionClient(credential)
        return credential, subscription_client
    except Exception as e:
        st.error(f"Failed to authenticate with Azure: {str(e)}")
        st.info("Please ensure you're logged in using 'az login'")
        return None, None

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

def display_parameters(parameters):
    """Display parameters in a formatted way"""
    if not parameters:
        st.info("No parameters set for this policy assignment")
        return

    st.write("Parameters:")
    for param_name, param_value in parameters.items():
        # Create a container for each parameter
        with st.container():
            # Use different styling for parameter name
            st.markdown(f"**{param_name}:**")

            # Handle different parameter value types
            if hasattr(param_value, 'value'):
                value = param_value.value
            else:
                value = param_value

            # Try to format as JSON if it's a dictionary or list
            try:
                if isinstance(value, (dict, list)):
                    st.json(value)
                else:
                    st.write(value)
            except:
                st.write(str(value))

            st.markdown("---")  # Add a separator between parameters

def main():
    st.title("Azure Policy Explorer")
    st.write("Explore Azure Policies across your subscriptions")

    # Initialize Azure connections
    with st.spinner("Connecting to Azure..."):
        credential, subscription_client = initialize_azure()

    if credential and subscription_client:
        # Get subscriptions
        subscriptions = get_subscriptions(subscription_client)

        if subscriptions:
            # Create subscription dropdown
            sub_options = {f"{sub.display_name} ({sub.subscription_id})": sub
                         for sub in subscriptions}
            selected_sub = st.selectbox(
                "Select Subscription",
                options=list(sub_options.keys())
            )

            if selected_sub:
                subscription = sub_options[selected_sub]
                st.write(f"Selected: {subscription.display_name}")

                # Show subscription details in an expander
                with st.expander("Subscription Details"):
                    st.write(f"Subscription ID: {subscription.subscription_id}")
                    st.write(f"State: {subscription.state}")
                    if hasattr(subscription, 'tenant_id'):
                        st.write(f"Tenant ID: {subscription.tenant_id}")

                # Get and display policy assignments
                st.subheader("Policy Assignments")
                with st.spinner("Fetching policy assignments..."):
                    policies = get_policy_assignments(credential, subscription.subscription_id)

                if policies:
                    for policy in policies:
                        with st.expander(f"📋 {policy.display_name or policy.name}"):
                            st.write(f"Name: {policy.name}")
                            if policy.description:
                                st.write(f"Description: {policy.description}")
                            st.write(f"Enforcement Mode: {policy.enforcement_mode}")
                            if policy.scope:
                                st.write(f"Scope: {policy.scope}")

                            # Display parameters section
                            st.markdown("---")
                            if hasattr(policy, 'parameters'):
                                display_parameters(policy.parameters)
                            else:
                                st.info("No parameters available for this policy assignment")
                else:
                    st.info("No policy assignments found for this subscription")

if __name__ == "__main__":
    main()
