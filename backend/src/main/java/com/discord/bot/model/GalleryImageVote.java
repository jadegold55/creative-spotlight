package com.discord.bot.model;

import jakarta.persistence.CascadeType;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.OnetoMany;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Table;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.UniqueConstraint;

import com.discord.bot.model.GalleryImage;

@Entity
@Table(name = "GalleryImageVotes", uniqueConstraints = {
        @UniqueConstraint(name = "Unique_Person_and_Unique_Image", columnNames = { "gallery_image_id", "userID" })
})
public class GalleryImageVote {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    @ManyToOne
    @JoinColumn(name = "gallery_image_id")
    private GalleryImage galleryImage;
    private Long userID;

    public GalleryImageVote() {
    }

    public GalleryImageVote(Long user, GalleryImage image) {
        this.userID = user;
        this.galleryImage = image;
    }

}
