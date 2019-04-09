def Content():
    APP_CONTENT = {
        "Home":[["Welcome", "/welcome/", "Welcome to my awesome app!", "welcome.jpg"],
               ["Background", "/background/", "This is where you can find out more about the app!", "background.jpg"],
               ["Messages", "/messages/", "Your user messages are waiting!", "messages.png"],],
        "Profile":[["User Profile", "/profile/", "Edit your profile here!", "profile.png"],
                  ["Settings", "/settings/", "App Settings, no biggie.", "settings.png"],
                  ["Terms of Service", "/tos/", "The legal stuff!", "tos.png"],],
        "Messages":[["Messages", "/messages/", "Your user messages are waiting!", "messages.png"],
                   ["Alerts", "/alerts/", "Urgent Alerts here!", "alerts.png"],],
        "Contact":[["Contact", "/contact/", "Contact us for support!", "contact.png"],],
    }
    return APP_CONTENT