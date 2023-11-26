from serverConn import main
from db import userValidation

validation = userValidation()

if validation == True:
    main()
else:
    print("The user credentials are invalid")