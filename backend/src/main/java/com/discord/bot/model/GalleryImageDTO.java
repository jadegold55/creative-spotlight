package com.discord.bot.model;

public class GalleryImageDTO {

    private Long id;
    private Long uploaderID;
    private Long guildid;
    private String contentType;
    private Long voteCount;
    private String title;

    public GalleryImageDTO(Long id, Long uploaderID, Long guildid, String contentType, String title, Long voteCount) {
        this.id = id;
        this.uploaderID = uploaderID;
        this.guildid = guildid;
        this.contentType = contentType;
        this.voteCount = voteCount;
        this.title = title;
    }

    public Long getId() {
        return id;
    }

    public Long getUploaderID() {
        return uploaderID;
    }

    public String getTitle() {
        return title;
    }

    public Long getGuildid() {
        return guildid;
    }

    public String getContentType() {
        return contentType;
    }

    public Long getVoteCount() {
        return voteCount;
    }
}
