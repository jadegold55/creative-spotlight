
package com.discord.bot.Controller;

import java.net.URI;
import java.util.List;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import com.discord.bot.Service.ContestSignupService;
import com.discord.bot.dto.ContestSignupsResponse;

@RestController
@RequestMapping("/contest_signups")
public class ContestController {
    private final ContestSignupService contestSignupService;

    public ContestController(ContestSignupService contestSignupService) {
        this.contestSignupService = contestSignupService;
    }

    @GetMapping("/{guildId}")
    public List<ContestSignupsResponse> getContestSignups(@PathVariable Long guildId) {
        return contestSignupService.getContestSignups(guildId);
    }

    @PostMapping("/{guildId}/signup")
    public ResponseEntity<ContestSignupsResponse> signupForContest(
            @PathVariable Long guildId,
            @RequestParam Long userId,
            @RequestParam String username,
            @RequestParam boolean isVerified) {
        ContestSignupsResponse created = contestSignupService.signupForContest(guildId, userId, username, isVerified);
        return ResponseEntity.created(URI.create("/contest_signups/" + guildId)).body(created);
    }

    @DeleteMapping("/{guildId}/signup")
    public ResponseEntity<Void> withdrawFromContest(@PathVariable Long guildId, @RequestParam Long userId) {
        contestSignupService.withdrawFromContest(guildId, userId);
        return ResponseEntity.noContent().build();
    }
}
