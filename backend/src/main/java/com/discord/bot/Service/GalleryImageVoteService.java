package com.discord.bot.Service;

import org.springframework.stereotype.Service;
import java.util.Optional;
import com.discord.bot.Exceptions.InvalidVote;
import com.discord.bot.Repository.GalleryImageVoteRepo;
import com.discord.bot.model.GalleryImage;
import com.discord.bot.model.GalleryImageVote;
import java.util.Optional;
import javax.lang.model.type.NullType;

import org.springframework.beans.factory.annotation.Autowired;

@Service
public class GalleryImageVoteService {
    private final GalleryImageVoteRepo galleryVoteRepo;

    public GalleryImageVoteService(GalleryImageVoteRepo galleryVoteRepo) {
        this.galleryVoteRepo = galleryVoteRepo;
    }

    public void addVote(Long userID, GalleryImage galleryimage) {
        if (galleryVoteRepo.findByUserIDAndGalleryImage(userID, galleryimage).isPresent()) {
            throw new InvalidVote("Unique ID must have Unique image ID");
        }
        galleryVoteRepo.save(new GalleryImageVote(userID, galleryimage));
    }

    public Long getVoteCount(GalleryImage image) {
        return galleryVoteRepo.countByGalleryImage(image);
    }

    public Optional<GalleryImage> getWinningImage(Long guildID) {
        return galleryVoteRepo.findWinningImageByGuild(guildID);
    }
}
