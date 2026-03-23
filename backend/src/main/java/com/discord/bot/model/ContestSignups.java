public class ContestSignups {
    private Long guildId;
    private Long id;

    private Long userId;
    private String username;
    private Long contestId;
    private Boolean isVerified;

    public ContestSignups() {
    }

    public ContestSignups(Long userId, Long contestId, Long guildId, String username, Boolean isVerified) {
        this.userId = userId;
        this.contestId = contestId;
        this.guildId = guildId;
        this.username = username;
        this.isVerified = isVerified;

    }

    public Long getGuildId() {
        return guildId;
    }

    public Long getId() {
        return id;
    }

    public Long getUserId() {
        return userId;
    }

    public String getUsername() {
        return username;
    }

}
