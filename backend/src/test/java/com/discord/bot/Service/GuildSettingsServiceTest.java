package com.discord.bot.Service;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import java.time.Duration;
import java.time.Instant;
import java.util.Optional;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.http.HttpStatus;
import org.springframework.web.server.ResponseStatusException;

import com.discord.bot.Repository.GuildSettingsRepo;
import com.discord.bot.dto.GuildSettingsResponse;
import com.discord.bot.dto.SetupContestRequest;
import com.discord.bot.model.GuildSettings;

@ExtendWith(MockitoExtension.class)
class GuildSettingsServiceTest {
    @Mock
    private GuildSettingsRepo guildSettingsRepo;

    private GuildSettingsService guildSettingsService;

    @BeforeEach
    void setUp() {
        guildSettingsService = new GuildSettingsService(guildSettingsRepo);
    }

    @Test
    void setupContestStoresOneTimeContestWindowAndMetadata() {
        Long guildId = 42L;
        SetupContestRequest request = new SetupContestRequest(123L, 5, 21, 0, "UTC", 3);

        when(guildSettingsRepo.findById(guildId)).thenReturn(Optional.empty());
        when(guildSettingsRepo.save(any(GuildSettings.class))).thenAnswer(invocation -> invocation.getArgument(0));

        GuildSettingsResponse response = guildSettingsService.setupContest(guildId, request);

        assertEquals(123L, response.spotlightChannelId());
        assertEquals(5, response.contestDay());
        assertEquals(21, response.contestHour());
        assertEquals(0, response.contestMinute());
        assertEquals("UTC", response.contestTimezone());
        assertEquals(3, response.contestDurationDays());
        assertNotNull(response.contestStartAt());
        assertNotNull(response.contestDeadlineAt());
        assertEquals(Duration.ofDays(3), Duration.between(response.contestStartAt(), response.contestDeadlineAt()));
    }

    @Test
    void setupContestRejectsInvalidTimezone() {
        SetupContestRequest request = new SetupContestRequest(123L, 5, 21, 0, "Mars/Phobos", 3);
        when(guildSettingsRepo.findById(42L)).thenReturn(Optional.empty());

        ResponseStatusException exception = assertThrows(
                ResponseStatusException.class,
                () -> guildSettingsService.setupContest(42L, request));

        assertEquals(HttpStatus.BAD_REQUEST, HttpStatus.valueOf(exception.getStatusCode().value()));
    }

    @Test
    void deleteContestSetupClearsStoredContestFields() {
        Long guildId = 42L;
        GuildSettings settings = new GuildSettings(guildId, 123L, null);
        settings.setContestDay(1);
        settings.setContestHour(21);
        settings.setContestMinute(0);
        settings.setContestTimezone("UTC");
        settings.setContestDurationDays(2);
        settings.setContestStartAt(Instant.parse("2026-04-03T21:00:00Z"));
        settings.setContestDeadlineAt(Instant.parse("2026-04-05T21:00:00Z"));

        when(guildSettingsRepo.findById(guildId)).thenReturn(Optional.of(settings));
        when(guildSettingsRepo.save(any(GuildSettings.class))).thenAnswer(invocation -> invocation.getArgument(0));

        guildSettingsService.deleteContestSetup(guildId);

        ArgumentCaptor<GuildSettings> captor = ArgumentCaptor.forClass(GuildSettings.class);
        verify(guildSettingsRepo).save(captor.capture());

        GuildSettings savedSettings = captor.getValue();
        assertNull(savedSettings.getSpotlightChannelId());
        assertNull(savedSettings.getContestDay());
        assertNull(savedSettings.getContestHour());
        assertNull(savedSettings.getContestMinute());
        assertNull(savedSettings.getContestTimezone());
        assertNull(savedSettings.getContestDurationDays());
        assertNull(savedSettings.getContestStartAt());
        assertNull(savedSettings.getContestDeadlineAt());
    }
}
