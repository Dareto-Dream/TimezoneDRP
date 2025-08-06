#include <discord.h>
#include <ctime>
#include <chrono>
#include <thread>
#include <iostream>

DiscordEventHandlers handlers;
DiscordRichPresence presence;

int main() {
    Discord_Initialize("YOUR_CLIENT_ID", &handlers, 1, NULL);

    time_t now = time(0);
    tm *local = gmtime(&now);
    local->tm_hour += 5;  // UTC+5 offset
    mktime(local);

    char timeStr[32];
    strftime(timeStr, sizeof(timeStr), "%H:%M %p", local);

    // Midnight UTC+5
    tm midnight = *local;
    midnight.tm_hour = 0;
    midnight.tm_min = 0;
    midnight.tm_sec = 0;
    time_t startTime = mktime(&midnight) - 5 * 3600;

    presence.details = timeStr;
    presence.state = "UTC+5";
    presence.startTimestamp = startTime;

    int hour = local->tm_hour;
    bool isDay = hour >= 6 && hour < 18;

    presence.largeImageKey  = isDay ? "clock_day" : "clock_night";
    presence.largeImageText = isDay ? "Daytime"    : "Nighttime";
    presence.smallImageKey  = isDay ? "clock_night": "clock_day";
    presence.smallImageText = isDay ? "Nighttime"  : "Daytime";

    Discord_UpdatePresence(&presence);

    std::cout << "Running DRP in C++ (Game SDK). Ctrl+C to exit.\n";
    while (true) {
        Discord_RunCallbacks();
        std::this_thread::sleep_for(std::chrono::seconds(15));
    }

    Discord_Shutdown();
    return 0;
}
