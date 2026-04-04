package com.discord.bot.Service;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import java.time.Instant;
import java.util.List;
import java.util.Optional;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.http.HttpStatus;
import org.springframework.web.server.ResponseStatusException;

import com.discord.bot.Repository.ContestSignupRepo;
import com.discord.bot.Repository.GuildSettingsRepo;
import com.discord.bot.dto.ContestSignupsResponse;
import com.discord.bot.model.ContestSignups;
import com.discord.bot.model.GuildSettings;

@ExtendWith(MockitoExtension.class)
class ContestSignupServiceTest {
    @Mock
    private ContestSignupRepo contestSignupRepo;

    @Mock
    private GuildSettingsRepo guildSettingsRepo;

    private ContestSignupService contestSignupService;

    @BeforeEach
    void setUp() {
        contestSignupService = new ContestSignupService(contestSignupRepo, guildSettingsRepo);
    }

    @Test
    void signupForContestStoresVerifiedSignupForCurrentContestWindow() {
        Long guildId = 42L;
        Long userId = 99L;
        Instant deadline = Instant.now().plusSeconds(3600);
        GuildSettings settings = buildGuildSettings(deadline);
        ContestSignups savedSignup = new ContestSignups(userId, guildId, "artist", true, deadline);

        when(guildSettingsRepo.findById(guildId)).thenReturn(Optional.of(settings));
        when(contestSignupRepo.existsByGuildIdAndUserIdAndSignupDeadlineAt(guildId, userId, deadline)).thenReturn(false);
        when(contestSignupRepo.save(any(ContestSignups.class))).thenReturn(savedSignup);

        ContestSignupsResponse response = contestSignupService.signupForContest(guildId, userId, "artist", true);

        ArgumentCaptor<ContestSignups> captor = ArgumentCaptor.forClass(ContestSignups.class);
        verify(contestSignupRepo).deleteByGuildIdAndSignupDeadlineAtLessThan(guildId, deadline);
        verify(contestSignupRepo).save(captor.capture());

        ContestSignups createdSignup = captor.getValue();
        assertEquals(userId, createdSignup.getUserId());
        assertEquals(guildId, createdSignup.getGuildId());
        assertEquals("artist", createdSignup.getUsername());
        assertTrue(createdSignup.isVerified());
        assertEquals(deadline, createdSignup.getSignupDeadlineAt());

        assertEquals(userId, response.userId());
        assertEquals(guildId, response.guildId());
        assertEquals("artist", response.username());
        assertTrue(response.isVerified());
        assertEquals(deadline, response.signupDeadlineAt());
    }

    @Test
    void signupForContestRejectsUnverifiedUsers() {
        ResponseStatusException exception = assertThrows(
                ResponseStatusException.class,
                () -> contestSignupService.signupForContest(42L, 99L, "artist", false));

        assertEquals(HttpStatus.FORBIDDEN, HttpStatus.valueOf(exception.getStatusCode().value()));
        verify(contestSignupRepo, never()).save(any());
    }

    @Test
    void signupForContestRejectsDuplicateSignup() {
        Long guildId = 42L;
        Long userId = 99L;
        Instant deadline = Instant.now().plusSeconds(3600);

        when(guildSettingsRepo.findById(guildId)).thenReturn(Optional.of(buildGuildSettings(deadline)));
        when(contestSignupRepo.existsByGuildIdAndUserIdAndSignupDeadlineAt(guildId, userId, deadline)).thenReturn(true);

        ResponseStatusException exception = assertThrows(
                ResponseStatusException.class,
                () -> contestSignupService.signupForContest(guildId, userId, "artist", true));

        assertEquals(HttpStatus.CONFLICT, HttpStatus.valueOf(exception.getStatusCode().value()));
    }

    @Test
    void getContestSignupsReturnsOnlyCurrentContestWindow() {
        Long guildId = 42L;
        Instant deadline = Instant.now().plusSeconds(3600);
        ContestSignups signup = new ContestSignups(99L, guildId, "artist", true, deadline);

        when(guildSettingsRepo.findById(guildId)).thenReturn(Optional.of(buildGuildSettings(deadline)));
        when(contestSignupRepo.findByGuildIdAndSignupDeadlineAtOrderByUsernameAsc(guildId, deadline))
                .thenReturn(List.of(signup));

        List<ContestSignupsResponse> results = contestSignupService.getContestSignups(guildId);

        assertEquals(1, results.size());
        assertEquals("artist", results.getFirst().username());
    }

    @Test
    void withdrawFromContestThrowsWhenSignupMissing() {
        Long guildId = 42L;
        Long userId = 99L;
        Instant deadline = Instant.now().plusSeconds(3600);

        when(guildSettingsRepo.findById(guildId)).thenReturn(Optional.of(buildGuildSettings(deadline)));
        when(contestSignupRepo.deleteByGuildIdAndUserIdAndSignupDeadlineAt(guildId, userId, deadline)).thenReturn(0L);

        ResponseStatusException exception = assertThrows(
                ResponseStatusException.class,
                () -> contestSignupService.withdrawFromContest(guildId, userId));

        assertEquals(HttpStatus.NOT_FOUND, HttpStatus.valueOf(exception.getStatusCode().value()));
    }

    @Test
    void signupForContestConvertsRepositoryConstraintViolationToConflict() {
        Long guildId = 42L;
        Long userId = 99L;
        Instant deadline = Instant.now().plusSeconds(3600);

        when(guildSettingsRepo.findById(guildId)).thenReturn(Optional.of(buildGuildSettings(deadline)));
        when(contestSignupRepo.existsByGuildIdAndUserIdAndSignupDeadlineAt(guildId, userId, deadline)).thenReturn(false);
        when(contestSignupRepo.save(any(ContestSignups.class))).thenThrow(new DataIntegrityViolationException("duplicate"));

        ResponseStatusException exception = assertThrows(
                ResponseStatusException.class,
                () -> contestSignupService.signupForContest(guildId, userId, "artist", true));

        assertEquals(HttpStatus.CONFLICT, HttpStatus.valueOf(exception.getStatusCode().value()));
    }

    @Test
    void isSignedUpChecksCurrentContestWindow() {
        Long guildId = 42L;
        Long userId = 99L;
        Instant deadline = Instant.now().plusSeconds(3600);

        when(guildSettingsRepo.findById(guildId)).thenReturn(Optional.of(buildGuildSettings(deadline)));
        when(contestSignupRepo.existsByGuildIdAndUserIdAndSignupDeadlineAt(guildId, userId, deadline)).thenReturn(true);

        assertTrue(contestSignupService.isSignedUp(guildId, userId));

        when(contestSignupRepo.existsByGuildIdAndUserIdAndSignupDeadlineAt(guildId, userId, deadline)).thenReturn(false);
        assertFalse(contestSignupService.isSignedUp(guildId, userId));
    }

    private GuildSettings buildGuildSettings(Instant deadline) {
        GuildSettings settings = new GuildSettings(42L, 123L, null);
        settings.setContestDeadlineAt(deadline);
        return settings;
    }
}
