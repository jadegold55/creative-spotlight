package com.discord.bot.Service;

import org.springframework.stereotype.Service;

import com.discord.bot.Exceptions.InvalidVote;
import com.discord.bot.Repository.GalleryImageVoteRepo;
import com.discord.bot.model.GalleryImage;
import com.discord.bot.model.GalleryImageVote;
import java.util.Optional;
import javax.lang.model.type.NullType;

import org.springframework.beans.factory.annotation.Autowired;

@Service
public class GalleryImageVoteService {
    @Autowired
    private GalleryImageVoteRepo gallery;

    public void addVote(Long userID, GalleryImage galleryimage) {

        Optional<GalleryImageVote> existingVote = gallery.findByUserIDAndGalleryImage(userID, galleryimage);
        if (existingVote.isPresent()) {
            throw new InvalidVote("Unique ID must have Unique image ID");
        } else {
            gallery.save(new GalleryImageVote(userID, galleryimage));

        }

    }

    public Long getVoteCount(GalleryImage image) {
        return gallery.countByGalleryImage(image);
    }

}
