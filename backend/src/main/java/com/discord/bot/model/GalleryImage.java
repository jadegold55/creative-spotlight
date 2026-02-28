package com.discord.bot.model;

import java.time.LocalDateTime;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Column;
import jakarta.persistence.Lob;

import com.fasterxml.jackson.annotation.JsonIgnore;
// gallery image has two differences here, one will be evenet based to schedule a dicosrd event where people can upload their pictures to the gallery so then what we
// want to do is when people view the gallery, lets let it be random and make sure that another pciture can't be seen in the gallery until all the pictures have been seen. so we can do this by having a list of picture ids that have been seen and then when we get a random picture, we check if it has been seen before and if it has, we get another random picture until we find one that hasn't been seen before. then we add that picture id to the list of seen pictures. once all pictures have been seen, we clear the list of seen pictures and start over. this way, we can ensure that all pictures are seen before any picture is seen again. the other difference is that we want to track who uploaded the picture and when it was uploaded so we can display that information in the gallery viewer.

//the second kind of gallery is for a protfoli that you can add to the bot which will communicate with teh front end at the same time. 
@Entity
public class GalleryImage {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private Long uploaderID;
    @Column(name = "guild_id")
    private Long guildid;
    private LocalDateTime uploadedAt;
    private String contentType;
    @JsonIgnore
    @Column(columnDefinition = "bytea")
    private byte[] imageData;

    public GalleryImage() {
    }

    // when imaage is created
    public GalleryImage(String contentType, byte[] imageData, Long uploaderID, Long guildid) {
        this.contentType = contentType;
        this.imageData = imageData;
        this.uploaderID = uploaderID;
        this.guildid = guildid;
        this.uploadedAt = LocalDateTime.now();
    }

    public Long getuploaderID() {
        return uploaderID;
    }

    public Long getGuildid() {
        return guildid;
    }

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public void setUploaderID(Long uploaderID) {
        this.uploaderID = uploaderID;
    }

    public void setGuildid(Long guildid) {
        this.guildid = guildid;
    }

    public String getContentType() {
        return contentType;
    }

    public void setContentType(String contentType) {
        this.contentType = contentType;
    }

    public byte[] getImageData() {
        return imageData;
    }

    public void setImageData(byte[] imageData) {
        this.imageData = imageData;
    }

    public LocalDateTime getUploadedAt() {
        return uploadedAt;
    }

    public void setUploadedAt(LocalDateTime uploadedAt) {
        this.uploadedAt = uploadedAt;
    }
}
