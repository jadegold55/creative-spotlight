package com.discord.bot.Service;

import java.time.DayOfWeek;
import java.time.ZoneId;
import java.time.ZonedDateTime;
import java.time.temporal.TemporalAdjusters;
import java.util.List;

import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ResponseStatusException;

import com.discord.bot.Repository.GuildSettingsRepo;
import com.discord.bot.dto.GuildSettingsResponse;
import com.discord.bot.dto.SetupChannelsRequest;
import com.discord.bot.dto.SetupContestRequest;
import com.discord.bot.dto.SetupPoemsRequest;
import com.discord.bot.model.GuildSettings;

@Service
public class GuildSettingsService {
    private final GuildSettingsRepo guildSettingsRepo;

    public GuildSettingsService(GuildSettingsRepo guildSettingsRepo) {
        this.guildSettingsRepo = guildSettingsRepo;
    }

    public GuildSettingsResponse getSettings(Long guildId) {
        return GuildSettingsResponse.from(getGuildOrThrow(guildId));
    }

    public GuildSettingsResponse setupPoems(Long guildId, SetupPoemsRequest request) {
        GuildSettings settings = getOrCreate(guildId);
        settings.setPoemChannelId(request.poemChannelId());
        settings.setPoemHour(request.hour());
        settings.setPoemMinute(request.minute());
        settings.setPoemTimezone(request.timezone());
        return GuildSettingsResponse.from(guildSettingsRepo.save(settings));
    }

    public GuildSettingsResponse setupContest(Long guildId, SetupContestRequest request) {
        GuildSettings settings = getOrCreate(guildId);
        ContestWindow contestWindow = calculateContestWindow(request);
        settings.setSpotlightChannelId(request.spotlightChannelId());
        settings.setContestStartAt(contestWindow.startAt());
        settings.setContestDeadlineAt(contestWindow.deadlineAt());
        return GuildSettingsResponse.from(guildSettingsRepo.save(settings));
    }

    public GuildSettingsResponse setupChannels(Long guildId, SetupChannelsRequest request) {
        GuildSettings settings = getOrCreate(guildId);
        if (request.poemChannelId() != null) {
            settings.setPoemChannelId(request.poemChannelId());
        }
        if (request.spotlightChannelId() != null) {
            settings.setSpotlightChannelId(request.spotlightChannelId());
        }

        return GuildSettingsResponse.from(guildSettingsRepo.save(settings));
    }

    public List<GuildSettingsResponse> getGuildsWithSpotlight() {
        return guildSettingsRepo.findBySpotlightChannelIdIsNotNull()
                .stream()
                .map(GuildSettingsResponse::from)
                .toList();
    }

    public List<GuildSettingsResponse> getGuildsWithPoems() {
        return guildSettingsRepo.findByPoemChannelIdIsNotNull()
                .stream()
                .map(GuildSettingsResponse::from)
                .toList();
    }

    public void deletePoemsSetup(Long guildId) {
        GuildSettings settings = getGuildOrThrow(guildId);
        settings.setPoemChannelId(null);
        settings.setPoemHour(null);
        settings.setPoemMinute(null);
        settings.setPoemTimezone(null);
        guildSettingsRepo.save(settings);
    }

    public void deleteContestSetup(Long guildId) {
        GuildSettings settings = getGuildOrThrow(guildId);
        settings.setSpotlightChannelId(null);
        settings.setContestStartAt(null);
        settings.setContestDeadlineAt(null);
        guildSettingsRepo.save(settings);
    }

    private ContestWindow calculateContestWindow(SetupContestRequest request) {
        ZoneId zoneId;
        try {
            zoneId = ZoneId.of(request.timezone());
        } catch (Exception ex) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Invalid contest timezone", ex);
        }

        ZonedDateTime now = ZonedDateTime.now(zoneId);
        ZonedDateTime contestStart = now
                .with(TemporalAdjusters.nextOrSame(toDayOfWeek(request.day())))
                .withHour(request.hour())
                .withMinute(request.minute())
                .withSecond(0)
                .withNano(0);

        if (!contestStart.isAfter(now)) {
            contestStart = contestStart.plusWeeks(1);
        }

        ZonedDateTime contestDeadline = contestStart.plusDays(request.durationDays());
        return new ContestWindow(contestStart.toInstant(), contestDeadline.toInstant());
    }

    private DayOfWeek toDayOfWeek(int configuredDay) {
        return DayOfWeek.of(configuredDay + 1);
    }

    private record ContestWindow(java.time.Instant startAt, java.time.Instant deadlineAt) {
    }

    private GuildSettings getOrCreate(Long guildId) {
        return guildSettingsRepo.findById(guildId)
                .orElse(new GuildSettings(guildId, null, null));
    }

    private GuildSettings getGuildOrThrow(Long guildId) {
        return guildSettingsRepo.findById(guildId)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Guild not configured"));
    }
}
