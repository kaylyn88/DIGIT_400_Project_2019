def Content():
    APP_CONTENT = {
        "Home":[["Welcome", "/welcome/", "Welcome to my awesome app!", "dancecat.gif"],
               ["Background", "/background/", "Learn more about the app here!", "dancecat.gif"],
               ["Messages", "/messages/", "Your user messages are waiting!", "dancecat.gif"],],
        "Profile":[["User Profile", "/profile/", "Edit your profile here!", "dancecat.gif"],
                  ["Settings", "/settings/", "App Settings, no biggie.", "dancecat.gif"],
                  ["Terms of Service", "/tos/", "The legal stuff!", "dancecat.gif"],],
        "Messages":[["Messages", "/messages/", "Your user messages are waiting!", "dancecat.gif"],
                   ["Alerts", "/alerts/", "Urgent Alerts here!", "dancecat.gif"],],
        "Contact":[["Contact", "/contact/", "Contact us for support!", "dancecat.gif"],],
    }
    return APP_CONTENT