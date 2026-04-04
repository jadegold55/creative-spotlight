package com.discord.bot.Service;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.Mockito.when;

import java.time.Instant;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.util.List;
import java.util.Optional;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.http.HttpStatus;
import org.springframework.web.server.ResponseStatusException;

import com.discord.bot.Repository.ContestSignupRepo;
import com.discord.bot.Repository.GalleryImageRepo;
import com.discord.bot.Repository.GalleryImageVoteRepo;
import com.discord.bot.Repository.GuildSettingsRepo;
import com.discord.bot.model.ContestSignups;
import com.discord.bot.model.ContestWinner;
import com.discord.bot.model.GalleryImage;
import com.discord.bot.model.GuildSettings;

@ExtendWith(MockitoExtension.class)
class GalleryImageServiceTest {
    @Mock
    private GalleryImageRepo galleryImageRepo;

    @Mock
    private GalleryImageVoteRepo galleryImageVoteRepo;

    @Mock
    private ContestSignupRepo contestSignupRepo;

    @Mock
    private GuildSettingsRepo guildSettingsRepo;

    private GalleryImageService galleryImageService;

    @BeforeEach
    void setUp() {
        galleryImageService = new GalleryImageService(
                galleryImageRepo,
                new GalleryImageVoteService(galleryImageVoteRepo),
                contestSignupRepo,
                guildSettingsRepo);
    }

    @Test
    void getContestWinnerReturnsHighestVotedEligibleContestImage() {
        Long guildId = 42L;
        Instant start = Instant.parse("2026-04-03T21:00:00Z");
        Instant deadline = Instant.parse("2026-04-04T21:00:00Z");
        GuildSettings settings = buildGuildSettings(start, deadline);

        ContestSignups firstSignup = new ContestSignups(100L, guildId, "alpha", true, deadline);
        ContestSignups secondSignup = new ContestSignups(200L, guildId, "beta", true, deadline);

        GalleryImage winningImage = buildImage(1L, 100L, guildId, start.plusSeconds(3600));
        GalleryImage lowerVoteImage = buildImage(2L, 200L, guildId, start.plusSeconds(7200));
        GalleryImage outOfWindowImage = buildImage(3L, 100L, guildId, start.minusSeconds(60));

        when(guildSettingsRepo.findById(guildId)).thenReturn(Optional.of(settings));
        when(contestSignupRepo.findByGuildIdAndSignupDeadlineAt(guildId, deadline))
                .thenReturn(List.of(firstSignup, secondSignup));
        when(galleryImageRepo.findByGuildIdAndUploaderIdIn(guildId, List.of(100L, 200L)))
                .thenReturn(List.of(lowerVoteImage, winningImage, outOfWindowImage));
        when(galleryImageVoteRepo.countByGalleryImage(winningImage)).thenReturn(8L);
        when(galleryImageVoteRepo.countByGalleryImage(lowerVoteImage)).thenReturn(5L);
        ContestWinner winner = galleryImageService.getContestWinner(guildId);

        assertEquals(1L, winner.getId());
        assertEquals(100L, winner.getUploaderId());
        assertEquals(8L, winner.getVotes());
    }

    @Test
    void getContestWinnerRejectsGuildWithoutContestWindow() {
        Long guildId = 42L;
        when(guildSettingsRepo.findById(guildId)).thenReturn(Optional.of(new GuildSettings(guildId, 123L, null)));

        ResponseStatusException exception = assertThrows(
                ResponseStatusException.class,
                () -> galleryImageService.getContestWinner(guildId));

        assertEquals(HttpStatus.CONFLICT, HttpStatus.valueOf(exception.getStatusCode().value()));
    }

    @Test
    void getContestWinnerRequiresAtLeastOneEligibleVotedSubmission() {
        Long guildId = 42L;
        Instant start = Instant.parse("2026-04-03T21:00:00Z");
        Instant deadline = Instant.parse("2026-04-04T21:00:00Z");
        GuildSettings settings = buildGuildSettings(start, deadline);

        ContestSignups signup = new ContestSignups(100L, guildId, "alpha", true, deadline);
        GalleryImage zeroVoteImage = buildImage(1L, 100L, guildId, start.plusSeconds(3600));

        when(guildSettingsRepo.findById(guildId)).thenReturn(Optional.of(settings));
        when(contestSignupRepo.findByGuildIdAndSignupDeadlineAt(guildId, deadline))
                .thenReturn(List.of(signup));
        when(galleryImageRepo.findByGuildIdAndUploaderIdIn(guildId, List.of(100L)))
                .thenReturn(List.of(zeroVoteImage));
        when(galleryImageVoteRepo.countByGalleryImage(zeroVoteImage)).thenReturn(0L);

        ResponseStatusException exception = assertThrows(
                ResponseStatusException.class,
                () -> galleryImageService.getContestWinner(guildId));

        assertEquals(HttpStatus.NOT_FOUND, HttpStatus.valueOf(exception.getStatusCode().value()));
    }

    private GuildSettings buildGuildSettings(Instant start, Instant deadline) {
        GuildSettings settings = new GuildSettings(42L, 123L, null);
        settings.setContestStartAt(start);
        settings.setContestDeadlineAt(deadline);
        return settings;
    }

    private GalleryImage buildImage(Long id, Long uploaderId, Long guildId, Instant uploadedAt) {
        GalleryImage image = new GalleryImage("image/png", new byte[] { 1 }, uploaderId, guildId);
        image.setId(id);
        image.setUploadedAt(LocalDateTime.ofInstant(uploadedAt, ZoneId.systemDefault()));
        image.setTitle("Entry " + id);
        return image;
    }
}
