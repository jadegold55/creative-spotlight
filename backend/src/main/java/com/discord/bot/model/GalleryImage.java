package com.discord.bot.model;

import java.time.LocalDateTime;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
// gallery image has two differences here, one will be evenet based to schedule a dicosrd event where people can upload their pictures to the gallery so then what we
// want to do is when people view the gallery, lets let it be random and make sure that another pciture can't be seen in the gallery until all the pictures have been seen. so we can do this by having a list of picture ids that have been seen and then when we get a random picture, we check if it has been seen before and if it has, we get another random picture until we find one that hasn't been seen before. then we add that picture id to the list of seen pictures. once all pictures have been seen, we clear the list of seen pictures and start over. this way, we can ensure that all pictures are seen before any picture is seen again. the other difference is that we want to track who uploaded the picture and when it was uploaded so we can display that information in the gallery viewer.

//the second kind of gallery is for a protfoli that you can add to the bot which will communicate with teh front end at the same time. 
@Entity
public class GalleryImage {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private long uploaderID;

    private LocalDateTime uploadedAt;
    private LocalDateTime contestDeadline;
    private Long contestId;

    private String url;

    public GalleryImage() {
    }

    // when imaage is created
    public GalleryImage(String url, long uploaderID) {
        this.url = url;
        this.uploaderID = uploaderID;
        this.uploadedAt = LocalDateTime.now();
        this.contestDeadline = this.uploadedAt.plusDays(7);
    }

    public GalleryImage(String url, long uploaderID, Long contestId, LocalDateTime contestDeadline) {
        this(url, uploaderID);
        this.contestId = contestId;
        this.contestDeadline = contestDeadline;
    }

    public GalleryImage(String url) {
        this.url = url;
    }

    public long getuploaderID() {
        return uploaderID;
    }

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getUrl() {
        return url;
    }

    public void setUploaderID(long uploaderID) {
        this.uploaderID = uploaderID;
    }

    public void setUrl(String url) {
        this.url = url;
    }

    public LocalDateTime getUploadedAt() {
        return uploadedAt;
    }

    public Long getContestId() {
        return contestId;
    }

    public void setContestId(Long contestId) {
        this.contestId = contestId;
    }

    public LocalDateTime getContestDeadline() {
        return contestDeadline;
    }

    public void setContestDeadline(LocalDateTime contestDeadline) {
        this.contestDeadline = contestDeadline;
    }

}
