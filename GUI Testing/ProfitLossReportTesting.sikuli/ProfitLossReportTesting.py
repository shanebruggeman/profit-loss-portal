##Test Login
find("1446597714942.png")
click("1446597724299.png")
type("user@gmail.com")
find("1446597752023.png")
click("1446597759404.png")
type("password")
find("1446597851312.png")
click("1446597862839.png")
if(exists("1446597929323.png")):
    print("Login Successfull")
else:
    print("Login failed")

##Test Generating Profit Loss Report
find("1446598155209.png")
click("1446598164438.png")
find("1446598198869.png")
click("1446598208571.png")
find("1446598230675.png")
click("1446598237536.png")

find("1446598218736.png")
click("1446598246853.png")
if(exists("1446598315492.png")):
    print("P&L Report Generated Successfully")
else:
    print("P&L Report Failed to Generate")