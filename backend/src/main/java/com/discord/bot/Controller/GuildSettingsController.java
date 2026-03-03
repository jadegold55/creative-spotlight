package com.discord.bot.Controller;

import com.discord.bot.Service.GuildSettingsService;
import com.discord.bot.dto.GuildSettingsResponse;
import com.discord.bot.dto.SetupChannelsRequest;
import com.discord.bot.dto.SetupContestRequest;
import com.discord.bot.dto.SetupPoemsRequest;
import java.util.List;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/guilds")
public class GuildSettingsController {
    private final GuildSettingsService guildSettingsService;

    public GuildSettingsController(GuildSettingsService guildSettingsService) {
        this.guildSettingsService = guildSettingsService;
    }

    @GetMapping("/{guildId}")
    public GuildSettingsResponse getSettings(@PathVariable Long guildId) {
        return guildSettingsService.getSettings(guildId);
    }

    @PostMapping("/{guildId}/setup-poems")
    public GuildSettingsResponse setupPoems(
            @PathVariable Long guildId,
            @RequestParam Long poemChannelId,
            @RequestParam Integer hour,
            @RequestParam Integer minute,
            @RequestParam String timezone) {
        return guildSettingsService.setupPoems(guildId,
                new SetupPoemsRequest(poemChannelId, hour, minute, timezone));
    }

    @PostMapping("/{guildId}/setup-contest")
    public GuildSettingsResponse setupContest(
            @PathVariable Long guildId,
            @RequestParam Long spotlightChannelId,
            @RequestParam Integer day,
            @RequestParam Integer hour,
            @RequestParam Integer minute,
            @RequestParam String timezone,
            @RequestParam Integer durationDays) {
        return guildSettingsService.setupContest(guildId,
                new SetupContestRequest(spotlightChannelId, day, hour, minute, timezone, durationDays));
    }

    @PostMapping("/{guildId}/setup")
    public GuildSettingsResponse setup(
            @PathVariable Long guildId,
            @RequestParam(required = false) Long poemChannelId,
            @RequestParam(required = false) Long spotlightChannelId) {
        return guildSettingsService.setupChannels(guildId,
                new SetupChannelsRequest(poemChannelId, spotlightChannelId));
    }

    @GetMapping("/with-spotlight")
    public List<GuildSettingsResponse> getGuildsWithSpotlight() {
        return guildSettingsService.getGuildsWithSpotlight();
    }

    @GetMapping("/with-poems")
    public List<GuildSettingsResponse> getGuildsWithPoems() {
        return guildSettingsService.getGuildsWithPoems();
    }

    @DeleteMapping("/{guildId}/setup-poems")
    public ResponseEntity<Void> deletePoemsSetup(@PathVariable Long guildId) {
        guildSettingsService.deletePoemsSetup(guildId);
        return ResponseEntity.noContent().build();
    }

    @DeleteMapping("/{guildId}/setup-contest")
    public ResponseEntity<Void> deleteContestSetup(@PathVariable Long guildId) {
        guildSettingsService.deleteContestSetup(guildId);
        return ResponseEntity.noContent().build();
    }
}