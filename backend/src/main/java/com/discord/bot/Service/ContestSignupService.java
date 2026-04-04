package com.discord.bot.Service;

import java.time.Instant;
import java.util.List;

import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ResponseStatusException;

import com.discord.bot.Repository.ContestSignupRepo;
import com.discord.bot.Repository.GuildSettingsRepo;
import com.discord.bot.dto.ContestSignupsResponse;
import com.discord.bot.model.ContestSignups;
import com.discord.bot.model.GuildSettings;

@Service
public class ContestSignupService {
    private final ContestSignupRepo contestSignupRepo;
    private final GuildSettingsRepo guildSettingsRepo;

    public ContestSignupService(ContestSignupRepo contestSignupRepo, GuildSettingsRepo guildSettingsRepo) {
        this.contestSignupRepo = contestSignupRepo;
        this.guildSettingsRepo = guildSettingsRepo;
    }

    public List<ContestSignupsResponse> getContestSignups(Long guildId) {
        Instant signupDeadlineAt = getContestDeadlineOrThrow(guildId);
        return contestSignupRepo.findByGuildIdAndSignupDeadlineAtOrderByUsernameAsc(guildId, signupDeadlineAt)
                .stream()
                .map(this::toResponse)
                .toList();
    }

    public ContestSignupsResponse signupForContest(Long guildId, Long userId, String username, boolean isVerified) {
        if (!isVerified) {
            throw new ResponseStatusException(HttpStatus.FORBIDDEN, "User must be Discord verified to sign up");
        }

        Instant signupDeadlineAt = getContestDeadlineOrThrow(guildId);
        purgeExpiredSignups(guildId, signupDeadlineAt);

        if (!signupDeadlineAt.isAfter(Instant.now())) {
            throw new ResponseStatusException(HttpStatus.CONFLICT, "Contest signups are closed for this guild");
        }

        if (contestSignupRepo.existsByGuildIdAndUserIdAndSignupDeadlineAt(guildId, userId, signupDeadlineAt)) {
            throw new ResponseStatusException(HttpStatus.CONFLICT, "User is already signed up for this guild");
        }

        ContestSignups signup = new ContestSignups(userId, guildId, username, true, signupDeadlineAt);
        try {
            return toResponse(contestSignupRepo.save(signup));
        } catch (DataIntegrityViolationException ex) {
            throw new ResponseStatusException(HttpStatus.CONFLICT, "User is already signed up for this guild", ex);
        }
    }

    public void withdrawFromContest(Long guildId, Long userId) {
        Instant signupDeadlineAt = getContestDeadlineOrThrow(guildId);
        long deletedRows = contestSignupRepo.deleteByGuildIdAndUserIdAndSignupDeadlineAt(guildId, userId, signupDeadlineAt);
        if (deletedRows == 0) {
            throw new ResponseStatusException(HttpStatus.NOT_FOUND, "Signup not found for this user in this guild");
        }
    }

    public boolean isSignedUp(Long guildId, Long userId) {
        Instant signupDeadlineAt = getContestDeadlineOrThrow(guildId);
        return contestSignupRepo.existsByGuildIdAndUserIdAndSignupDeadlineAt(guildId, userId, signupDeadlineAt);
    }

    private ContestSignupsResponse toResponse(ContestSignups signup) {
        return new ContestSignupsResponse(
                signup.getId(),
                signup.getUserId(),
                signup.getGuildId(),
                signup.getUsername(),
                signup.isVerified(),
                signup.getSignupDeadlineAt());
    }

    private void purgeExpiredSignups(Long guildId, Instant signupDeadlineAt) {
        contestSignupRepo.deleteByGuildIdAndSignupDeadlineAtLessThan(guildId, signupDeadlineAt);
    }

    private Instant getContestDeadlineOrThrow(Long guildId) {
        GuildSettings settings = guildSettingsRepo.findById(guildId)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Guild not configured"));

        if (settings.getContestDeadlineAt() == null) {
            throw new ResponseStatusException(HttpStatus.CONFLICT, "Contest is not configured for this guild");
        }

        return settings.getContestDeadlineAt();
    }
}
