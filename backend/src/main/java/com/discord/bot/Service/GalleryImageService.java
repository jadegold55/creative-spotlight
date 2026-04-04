package com.discord.bot.Service;

import com.discord.bot.Repository.ContestSignupRepo;
import com.discord.bot.Repository.GalleryImageRepo;
import com.discord.bot.Repository.GuildSettingsRepo;
import com.discord.bot.dto.GalleryImageResponse;
import com.discord.bot.model.ContestSignups;
import com.discord.bot.model.ContestWinner;
import com.discord.bot.model.GalleryImage;
import com.discord.bot.model.GuildSettings;
import java.io.IOException;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.UUID;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.server.ResponseStatusException;

@Service
public class GalleryImageService {
    private final GalleryImageRepo galleryImageRepo;
    private final GalleryImageVoteService galleryImageVoteService;
    private final ContestSignupRepo contestSignupRepo;
    private final GuildSettingsRepo guildSettingsRepo;

    public GalleryImageService(
            GalleryImageRepo galleryImageRepo,
            GalleryImageVoteService galleryImageVoteService,
            ContestSignupRepo contestSignupRepo,
            GuildSettingsRepo guildSettingsRepo) {
        this.galleryImageRepo = galleryImageRepo;
        this.galleryImageVoteService = galleryImageVoteService;
        this.contestSignupRepo = contestSignupRepo;
        this.guildSettingsRepo = guildSettingsRepo;
    }

    public GalleryImageResponse getImage(Long id) {
        GalleryImage image = getImageOrThrow(id);
        return toResponse(image, galleryImageVoteService.getVoteCount(image));
    }

    public List<GalleryImageResponse> getAllImages(Long guildId) {
        return galleryImageRepo.findByGuildIdWithVotes(guildId);
    }

    public ContestWinner getContestWinner(Long guildId) {
        GuildSettings settings = guildSettingsRepo.findById(guildId)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Guild not configured"));
        if (settings.getContestStartAt() == null || settings.getContestDeadlineAt() == null) {
            throw new ResponseStatusException(HttpStatus.CONFLICT, "Contest is not configured for this guild");
        }

        List<Long> eligibleUploaderIds = contestSignupRepo
                .findByGuildIdAndSignupDeadlineAt(guildId, settings.getContestDeadlineAt())
                .stream()
                .map(ContestSignups::getUserId)
                .distinct()
                .toList();

        if (eligibleUploaderIds.isEmpty()) {
            throw new ResponseStatusException(HttpStatus.NOT_FOUND, "No contest winner found");
        }

        LocalDateTime contestStart = LocalDateTime.ofInstant(settings.getContestStartAt(), ZoneId.systemDefault());
        LocalDateTime contestDeadline = LocalDateTime.ofInstant(settings.getContestDeadlineAt(), ZoneId.systemDefault());

        GalleryImage winner = galleryImageRepo.findByGuildIdAndUploaderIdIn(guildId, eligibleUploaderIds)
                .stream()
                .filter(image -> !image.getUploadedAt().isBefore(contestStart))
                .filter(image -> !image.getUploadedAt().isAfter(contestDeadline))
                .filter(image -> galleryImageVoteService.getVoteCount(image) > 0)
                .max(Comparator
                        .comparingLong((GalleryImage image) -> galleryImageVoteService.getVoteCount(image))
                        .thenComparing(GalleryImage::getUploadedAt))
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "No contest winner found"));
        return new ContestWinner(winner.getId(), winner.getUploaderId(), galleryImageVoteService.getVoteCount(winner));
    }

    public List<GalleryImageResponse> getImagesByUploader(Long uploaderId, Long guildId) {
        return galleryImageRepo.findByUploaderIdAndGuildId(uploaderId, guildId)
                .stream()
                .map(image -> toResponse(image, galleryImageVoteService.getVoteCount(image)))
                .toList();
    }

    public GalleryImageResponse addImage(MultipartFile file, Long uploaderId, Long guildId, String title) {
        try {
            GalleryImage image = new GalleryImage(file.getContentType(), file.getBytes(), uploaderId, guildId);
            image.setTitle(title != null ? title : "Untitled");
            GalleryImage saved = galleryImageRepo.save(image);
            return toResponse(saved, 0L);
        } catch (IOException e) {
            throw new ResponseStatusException(HttpStatus.INTERNAL_SERVER_ERROR, "Failed to read image file", e);
        }
    }

    public List<GalleryImageResponse> addImages(List<MultipartFile> files, Long uploaderId, Long guildId,
            String title) {
        String groupId = UUID.randomUUID().toString();
        List<GalleryImageResponse> responses = new ArrayList<>();
        for (MultipartFile file : files) {
            try {
                GalleryImage image = new GalleryImage(file.getContentType(), file.getBytes(), uploaderId, guildId,
                        groupId);
                image.setTitle(title != null ? title : "Untitled");
                GalleryImage saved = galleryImageRepo.save(image);
                responses.add(toResponse(saved, 0L));
            } catch (IOException e) {
                throw new ResponseStatusException(HttpStatus.INTERNAL_SERVER_ERROR, "Failed to read image file", e);
            }
        }
        return responses;
    }

    public void vote(Long id, Long userId) {
        galleryImageVoteService.addVote(userId, getImageOrThrow(id));
    }

    public void deleteImage(Long id) {
        galleryImageRepo.delete(getImageOrThrow(id));
    }

    public GalleryImage getImageOrThrow(Long id) {
        return galleryImageRepo.findById(id)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Image not found with id " + id));
    }

    private GalleryImageResponse toResponse(GalleryImage image, Long voteCount) {
        return new GalleryImageResponse(
                image.getId(),
                image.getUploaderId(),
                image.getGuildId(),
                image.getTitle(),
                image.getContentType(),
                image.getUploadedAt(),
                voteCount,
                image.getGroupId());
    }
}
