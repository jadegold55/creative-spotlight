
package com.discord.bot.Controller;

import java.util.List;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/contest_signups")
public class ContestController {

    @GetMapping("/{guildId}")
    public Long getContestSignups(@PathVariable Long guildId) {
        return null;
    }

    @PostMapping("/{guildId}/signup")
    public ResponseEntity<String> signupForContest(@PathVariable Long guildId, @RequestParam Long userId,
            @RequestParam String username) {
        return ResponseEntity.ok("User signed up for contest");
    }

    @DeleteMapping("/{guildId}/signup")
    public ResponseEntity<String> withdrawFromContest(@PathVariable Long guildId, @RequestParam Long userId) {
        return ResponseEntity.ok("User withdrawn from contest");
    }
}
