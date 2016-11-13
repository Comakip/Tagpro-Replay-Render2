map_codes = {
        "0" : "black",
        "1" : "wall",
        "1.2" : "225 tile",
        "1.3" : "135 tile",
        "1.4" : "45 tile",
        "1.1" : "315 tile",
        "2" : "floor",
        "3" : "red flag",
        "3.1" : "red flag away",
        "4" : "blue flag",
        "4.1" : "blue flag away",
        "5" : "boost",
        "5.1" : "boost off", 
        "6" : "powerup off",
        "6.3" : "tagpro",
        "6.1" : "jukejuice", 
        "6.2" : "rolling bomb",
        "7" : "spike",
        "8" : "button",
        "9" : "gate off",
        "9.1" : "gate neutral",
        "9.2" : "gate red",
        "9.3" : "gate blue",
        "10" : "bomb",
        "10.1" : "bomb off",
        "11" : "red speed",
        "12" : "blue speed",
        "13" : "portal",
        "13.1" : "portal off",
        "14" : "red boost",
        "14.1" : "red boost off", 
        "15" : "blue boost",
        "15.1" : "blue boost off",
        "16" : "neutral flag",
        "16.1" : "neutral flag away",
        "17" : "red endzone",
        "18" : "blue endzone"
}

tiles_map = {
        "spike" : (480, 0),
        "red ball" : (560, 0),
        "blue ball" : (600, 0),
        "bomb" : (480, 40),
        "bomb off" : (480, 80),
        "neutral flag" : (520, 40),
        "neutral flag away" : (520, 80),
        "red flag" : (560, 40),
        "red flag away" : (560, 80),
        "blue flag" : (600, 40),
        "blue flag away" : (600, 80),
        "gate off" : (480, 120),
        "gate neutral" : (520, 120),
        "gate red" : (560, 120),
        "gate blue" : (600, 120),
        "floor" : (520, 160),
        "red speed" : (560, 160),
        "blue speed" : (600, 160),
        "red endzone" : (560, 200),
        "blue endzone" : (600, 200),
        "button" : (520, 240),
        "black" : (560, 360),
        "wall" : (600, 240),
        "tagpro" : (480, 240),
        "jukejuice" : (480, 160),
        "rolling bomb" : (480, 200),
        "powerup off" :  (480, 320),
        "315 tile" : (600, 280),
        "45 tile" : (600, 320),
        "225 tile" : (600, 360), 
        "135 tile" : (600, 400), 
        "mars ball" : (480, 360),
        }
portal_map = {
        "portal" : ((0, 0), (40, 0), (80, 0), (120, 0)), 
        "portal off" : (160, 0)
        }

boost_map = {
        "boost" :  ((0, 0), (40, 0), (80, 0), (120, 0)),
        "boost off" : (160, 0)
        }

boost_red_map = {
        "red boost" :  ((0, 0), (40, 0), (80, 0), (120, 0)),
        "red boost off" : (160, 0)
        }

boost_blue_map = {
        "blue boost" :  ((0, 0), (40, 0), (80, 0), (120, 0)),
        "blue boost off" : (160, 0)
        }
