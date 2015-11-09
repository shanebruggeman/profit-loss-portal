##Test Login
find("1446578677816.png")
click("1446578714024.png")
type("user@gmail.com")
find("1446578734600.png")
click("1446578746219.png")
type("password")
find("1446578792088.png")
click("1446578800553.png")
if(exists("1446578850378.png")):
    print("Login passed");
else:
    print("Login failed");

##Test Generating Trader Confirmation Report
find("1446579139065.png")
click("1446579216809.png")
find("1446579854463.png")
click("1446579871170.png")
find("1446579237922.png")
click("1446579897330.png")
find("1446579906548.png")
click("1446579914227.png")

if(exists("1446579686089.png")):
    print("TCR generated successfully")
else:
    print("TCR failed to generate")

##Testing generating a graph from TCR
find("1446580303344.png")
click("1446580313354.png")
type("ASHR")
find("1446580328096.png")
click("1446580351446.png")
wait(5)
if(exists("1446580709447.png")):##Values subject to change
    print("Chart generated successfully")
else:
    print("Chart failed to generate")

##Testing Hide Chart
find("1446580467731.png")
click("1446580475774.png")

if(exists("1446580554730.png")):
    print("Chart Hidden Successfully")
else:
    print("Chart not hidden")

##Testing Logout
find("1446647614497.png")
click("1446647623594.png")
if(exists("1446647672309.png")):
    print("Logout Successful")
else:
    print("Logout Failed")

    



    
    