package com.discord.bot.model;

public class ContestWinner {
    private String url;
    private Long uploaderid;
    private Long votes;

    public ContestWinner(String url, Long uploaderid, Long votes) {
        this.url = url;
        this.uploaderid = uploaderid;
        this.votes = votes;
    }

    public String getUrl() {
        return url;
    }

    public Long getUploaderid() {
        return uploaderid;
    }

    public Long getVotes() {
        return votes;
    }
}
