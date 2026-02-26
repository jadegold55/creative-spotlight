package com.discord.bot.Controller;

import com.discord.bot.Repository.GuildSettingsRepo;
import com.discord.bot.model.GuildSettings;

import java.util.List;

import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;

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
