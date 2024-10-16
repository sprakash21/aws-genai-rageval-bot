### Operations activity post deployment of the stack

#### Set Permanent Password for the User
A user is temporarily created during the deployment of the stack and to permanently set the password we use the 
script `create_permanent.user.py` which takes arguments as username, user_pool_id, and region.  
To run this:
```
First export the region using export AWS_PROFILE=<Your Profile>
Then run python3 set_permanent_password.py --username <username> --pool_id <pool_id> --region <region>
This will return the permanent password created to gain access to the application.
```
