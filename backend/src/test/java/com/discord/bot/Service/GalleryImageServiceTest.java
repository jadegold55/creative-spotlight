package com.discord.bot.Service;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import java.time.Instant;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.util.List;
import java.util.Optional;
import java.util.concurrent.atomic.AtomicLong;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.http.HttpStatus;
import org.springframework.mock.web.MockMultipartFile;
import org.springframework.web.server.ResponseStatusException;

import com.discord.bot.Repository.ContestSignupRepo;
import com.discord.bot.Repository.GalleryImageRepo;
import com.discord.bot.Repository.GalleryImageVoteRepo;
import com.discord.bot.Repository.GuildSettingsRepo;
import com.discord.bot.dto.GalleryImageResponse;
import com.discord.bot.model.ContestSignups;
import com.discord.bot.model.ContestWinner;
import com.discord.bot.model.GalleryImage;
import com.discord.bot.model.GalleryImageVote;
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

    @Test
    void addImageDefaultsMissingTitleAndReturnsResponse() {
        MockMultipartFile file = new MockMultipartFile("file", "art.png", "image/png", new byte[] { 1, 2 });

        when(galleryImageRepo.save(any(GalleryImage.class))).thenAnswer(invocation -> {
            GalleryImage image = invocation.getArgument(0);
            image.setId(10L);
            return image;
        });

        GalleryImageResponse response = galleryImageService.addImage(file, 99L, 42L, null);

        ArgumentCaptor<GalleryImage> captor = ArgumentCaptor.forClass(GalleryImage.class);
        verify(galleryImageRepo).save(captor.capture());

        GalleryImage savedImage = captor.getValue();
        assertEquals("Untitled", savedImage.getTitle());
        assertEquals("image/png", savedImage.getContentType());
        assertEquals(99L, savedImage.getUploaderId());
        assertEquals(42L, savedImage.getGuildId());
        assertNotNull(savedImage.getGroupId());

        assertEquals(10L, response.id());
        assertEquals("Untitled", response.title());
        assertEquals(0L, response.voteCount());
        assertEquals(savedImage.getGroupId(), response.groupId());
    }

    @Test
    void addImagesStoresBatchWithSharedGroupIdAndTitle() {
        MockMultipartFile firstFile = new MockMultipartFile("files", "one.png", "image/png", new byte[] { 1 });
        MockMultipartFile secondFile = new MockMultipartFile("files", "two.png", "image/png", new byte[] { 2 });
        AtomicLong nextId = new AtomicLong(20L);

        when(galleryImageRepo.save(any(GalleryImage.class))).thenAnswer(invocation -> {
            GalleryImage image = invocation.getArgument(0);
            image.setId(nextId.getAndIncrement());
            return image;
        });

        List<GalleryImageResponse> responses = galleryImageService.addImages(
                List.of(firstFile, secondFile),
                99L,
                42L,
                "Portfolio");

        ArgumentCaptor<GalleryImage> captor = ArgumentCaptor.forClass(GalleryImage.class);
        verify(galleryImageRepo, times(2)).save(captor.capture());

        List<GalleryImage> savedImages = captor.getAllValues();
        String groupId = savedImages.getFirst().getGroupId();
        assertNotNull(groupId);
        assertEquals(groupId, savedImages.get(1).getGroupId());
        assertEquals("Portfolio", savedImages.getFirst().getTitle());
        assertEquals("Portfolio", savedImages.get(1).getTitle());

        assertEquals(2, responses.size());
        assertEquals(groupId, responses.getFirst().groupId());
        assertEquals(groupId, responses.get(1).groupId());
    }

    @Test
    void getImagesByUploaderMapsImagesWithVoteCounts() {
        GalleryImage firstImage = buildImage(1L, 99L, 42L, Instant.parse("2026-04-03T21:00:00Z"));
        GalleryImage secondImage = buildImage(2L, 99L, 42L, Instant.parse("2026-04-03T22:00:00Z"));

        when(galleryImageRepo.findByUploaderIdAndGuildId(99L, 42L)).thenReturn(List.of(firstImage, secondImage));
        when(galleryImageVoteRepo.countByGalleryImage(firstImage)).thenReturn(3L);
        when(galleryImageVoteRepo.countByGalleryImage(secondImage)).thenReturn(0L);

        List<GalleryImageResponse> responses = galleryImageService.getImagesByUploader(99L, 42L);

        assertEquals(2, responses.size());
        assertEquals(1L, responses.getFirst().id());
        assertEquals(3L, responses.getFirst().voteCount());
        assertEquals(2L, responses.get(1).id());
        assertEquals(0L, responses.get(1).voteCount());
    }

    @Test
    void voteLoadsImageAndDelegatesToVoteRepository() {
        GalleryImage image = buildImage(1L, 99L, 42L, Instant.parse("2026-04-03T21:00:00Z"));

        when(galleryImageRepo.findById(1L)).thenReturn(Optional.of(image));
        when(galleryImageVoteRepo.findByUserIdAndGalleryImage(123L, image)).thenReturn(Optional.empty());

        galleryImageService.vote(1L, 123L);

        verify(galleryImageVoteRepo).save(any(GalleryImageVote.class));
    }

    @Test
    void deleteImageDeletesLoadedImage() {
        GalleryImage image = buildImage(1L, 99L, 42L, Instant.parse("2026-04-03T21:00:00Z"));
        when(galleryImageRepo.findById(1L)).thenReturn(Optional.of(image));

        galleryImageService.deleteImage(1L);

        verify(galleryImageRepo).delete(image);
    }

    @Test
    void deleteImageThrowsNotFoundWhenImageMissing() {
        when(galleryImageRepo.findById(1L)).thenReturn(Optional.empty());

        ResponseStatusException exception = assertThrows(
                ResponseStatusException.class,
                () -> galleryImageService.deleteImage(1L));

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
