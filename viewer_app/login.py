import ldap3

class CheckLogin:
    """Check the user's ADS credentials
    """
    def check_login(username:str, password:str) -> bool:
        """Check the user's ADS credentials passed as inputs

        Args:
            username (str): Text entered as username
            password (str): Text entered as password

        Returns:
            bool: Correctly registered or not
        """""
        is_logged = False
        # URL of the LDAP server (case for German DS environment, change it for spanish to ldaps://eadscasa.casa.corp:636)
        ldap_auth_url = "ldaps://eadscasa.casa.corp:636"

        # LDAP bind credentials
        # ONLY FOR PRODUCTION: REQUEST CREDENTIALS THROUGH MYITSM (talk to Samuel Perez Oses for Spain - ideally request new ones per project)
        # FOR LOCAL APPS: ldap_auth_bind_dn = "eadscasa\\CXXXXX" ldap_auth_bind_password = "windows_password"
        ldap_auth_bind_dn = f"eadscasa\\{username}"
        ldap_auth_bind_password = f"{password}"

        # ldap_auth_bind_dn = "mmain\\SvcDEPCIN_Control"
        # ldap_auth_bind_password = "J82ln8YqRtZg9sLw5?7-lw3pb"

        # LDAP user search settings
        ldap_auth_search_base = 'OU=Persons,DC=eadscasa,DC=casa,DC=corp'
        ldap_auth_search_scope = ldap3.SUBTREE

        # Username lookup settings
        ldap_auth_object_class = "user"
        ldap_auth_user_fields = "sAMAccountName"

        # User to authenticate
        user_username = f"{username}"
        user_password = f"{password}"

        # Create an LDAP connection
        try:
            server = ldap3.Server(ldap_auth_url)
            connection = ldap3.Connection(
                server,
                user=ldap_auth_bind_dn,
                password=ldap_auth_bind_password,
                auto_bind=True,
            )

            if connection:
                print("connected to LDAP*********")

            # Define the base DN and search filter to find the user by username
            search_base = ldap_auth_search_base  # Adjust the base DN to match your LDAP directory structure
            search_filter = f"(&(objectClass={ldap_auth_object_class})({ldap_auth_user_fields}={user_username}))"

            # Specify the search scope as SUBTREE to search the entire subtree
            search_scope = ldap_auth_search_scope

            # Specify the attributes to retrieve
            attributes_to_retrieve = [
                "sAMAccountName",
                "mail",
                "givenName",
                "sn",
                "userPassword",
            ]

            # Perform an LDAP search to find the user by username and retrieve information
            connection.search(
                search_base,
                search_filter,
                search_scope,
                attributes=attributes_to_retrieve,
            )

            # Check if the user was found
            if connection.entries:
                # Get the DN of the user entry
                user_dn = connection.entries[0].entry_dn
                print(f"LDAP Information for user {user_username} is: {user_dn}\n")

                # Attempt to bind (authenticate) as the user
                try:
                    user_connection = ldap3.Connection(
                        server, user=user_dn, password=user_password, auto_bind=True
                    )
                    is_logged = True
                except:
                    is_logged = False
            else:
                print("not connected*******º")

            # Close the main LDAP connection
            connection.unbind()
        except:
            print("failed to connect")
            pass

        return is_logged