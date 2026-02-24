package com.discord.bot.Service;

import org.springframework.stereotype.Service;

import com.discord.bot.Exceptions.InvalidVote;
import com.discord.bot.Repository.GalleryImageVoteRepo;
import com.discord.bot.model.GalleryImage;
import com.discord.bot.model.GalleryImageVote;

import main.java.com.discord.bot.Service.GalleryImageVoteService.ContestWinner;

import com.discord.bot.Repository.GalleryImageRepo;
import com.discord.bot.Exceptions.VotingClosedException;
import java.time.LocalDateTime;
import java.util.Optional;
import javax.lang.model.type.NullType;
import java.time.LocalDateTime;
import org.springframework.beans.factory.annotation.Autowired;
import java.time.LocalDateTime;

import org.springframework.http.HttpStatus;
import org.springframework.web.server.ResponseStatusException;

@Service
public class GalleryImageVoteService {
    private final GalleryImageVoteRepo galleryVoteRepo;

    private final GalleryImageRepo galleryImageRepo;

    public GalleryImageVoteService(GalleryImageVoteRepo galleryVoteRepo, GalleryImageRepo galleryImageRepo) {
        this.galleryVoteRepo = galleryVoteRepo;
        this.galleryImageRepo = galleryImageRepo;
    }

    public record ContestWinner(Long imageId, String imageUrl, Long uploaderId, Long voteCount) {
    }

    public void addVote(Long userID, GalleryImage galleryimage) {
        if (galleryimage.getContestDeadline() != null
                && LocalDateTime.now().isAfter(galleryimage.getContestDeadline())) {
            throw new VotingClosedException("Voting is closed for this contest");
        }
        if (galleryVoteRepo.findByUserIDAndGalleryImage(userID, galleryimage).isPresent()) {
            throw new InvalidVote("Unique ID must have Unique image ID");
        }
        galleryVoteRepo.save(new GalleryImageVote(userID, galleryimage));
    }

    public Long getVoteCount(GalleryImage image) {
        return galleryVoteRepo.countByGalleryImage(image);
    }

    public ContestWinner getWinningImageForContest(Long contestId) {
        GalleryImage contestInfo = galleryImageRepo.findFirstByContestIdOrderByContestDeadlineAscIdAsc(contestId)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND,
                        "No valid submissions found for contest " + contestId));

        LocalDateTime contestDeadline = contestInfo.getContestDeadline();
        if (contestDeadline == null) {
            throw new ResponseStatusException(HttpStatus.UNPROCESSABLE_ENTITY,
                    "Contest " + contestId + " does not have a configured deadline");
        }

        if (contestDeadline.isAfter(LocalDateTime.now())) {
            throw new ResponseStatusException(HttpStatus.CONFLICT,
                    "Contest " + contestId + " is still active");
        }

        return galleryVoteRepo.findContestVoteTotalsOrderByWinnerRules(contestId)
                .stream()
                .findFirst()
                .map(result -> new ContestWinner(
                        result.getImageId(),
                        result.getImageUrl(),
                        result.getUploaderID(),
                        result.getVoteCount()))
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND,
                        "No valid submissions found for contest " + contestId));
    }
}
