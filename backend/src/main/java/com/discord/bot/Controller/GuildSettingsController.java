package com.discord.bot.Controller;

import com.discord.bot.Repository.GuildSettingsRepo;
import com.discord.bot.model.GuildSettings;

import java.util.List;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;

@RestController
@RequestMapping("/guilds")
public class GuildSettingsController {
    private final GuildSettingsRepo guildSettingsRepo;

    public GuildSettingsController(GuildSettingsRepo guildSettingsRepo) {
        this.guildSettingsRepo = guildSettingsRepo;
    }

    @GetMapping("/{guildId}")
    public GuildSettings getSettings(@PathVariable Long guildId) {
        return guildSettingsRepo.findById(guildId)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Guild not configured"));
    }

    @PostMapping("/{guildId}/setup-poems")
    public GuildSettings setupPoems(
            @PathVariable Long guildId,
            @RequestParam Long poemChannelId,
            @RequestParam Integer hour,
            @RequestParam Integer minute,
            @RequestParam String timezone) {

        GuildSettings settings = guildSettingsRepo.findById(guildId)
                .orElse(new GuildSettings(guildId, null, null));

        settings.setPoemChannelId(poemChannelId);
        settings.setPoemHour(hour);
        settings.setPoemMinute(minute);
        settings.setPoemTimezone(timezone);

        return guildSettingsRepo.save(settings);
    }

    @PostMapping("/{guildId}/setup-contest")
    public GuildSettings setupContest(
            @PathVariable Long guildId,
            @RequestParam Long spotlightChannelId,
            @RequestParam Integer day,
            @RequestParam Integer hour,
            @RequestParam Integer minute,
            @RequestParam String timezone,
            @RequestParam Integer durationDays) {

        GuildSettings settings = guildSettingsRepo.findById(guildId)
                .orElse(new GuildSettings(guildId, null, null));

        settings.setSpotlightChannelId(spotlightChannelId);
        settings.setContestDay(day);
        settings.setContestHour(hour);
        settings.setContestMinute(minute);
        settings.setContestTimezone(timezone);
        settings.setContestDurationDays(durationDays);

        return guildSettingsRepo.save(settings);
    }

    @PostMapping("/{guildId}/setup")
    public GuildSettings setup(
            @PathVariable Long guildId,
            @RequestParam(required = false) Long poemChannelId,
            @RequestParam(required = false) Long spotlightChannelId) {

        GuildSettings settings = guildSettingsRepo.findById(guildId)
                .orElse(new GuildSettings(guildId, null, null));

        if (poemChannelId != null)
            settings.setPoemChannelId(poemChannelId);
        if (spotlightChannelId != null)
            settings.setSpotlightChannelId(spotlightChannelId);

        return guildSettingsRepo.save(settings);
    }

    @GetMapping("/with-spotlight")
    public List<GuildSettings> getGuildsWithSpotlight() {
        return guildSettingsRepo.findBySpotlightChannelIdIsNotNull();
    }

    @GetMapping("/with-poems")
    public List<GuildSettings> getGuildsWithPoems() {
        return guildSettingsRepo.findByPoemChannelIdIsNotNull();
    }
}
