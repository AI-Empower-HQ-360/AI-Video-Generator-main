const { test, expect } = require('@playwright/test');

test.describe('AI Empower Heart E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Mock API responses to avoid external dependencies
    await page.route('**/api/**', route => {
      const url = route.request().url();
      
      if (url.includes('/api/spiritual/guidance')) {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            response: 'Thank you for your question about karma yoga. Karma yoga is the path of selfless action...',
            guru_type: 'karma'
          })
        });
      } else if (url.includes('/api/users/register')) {
        route.fulfill({
          status: 201,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            message: 'Registration successful',
            user_id: 'user_123'
          })
        });
      } else if (url.includes('/api/users/login')) {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            message: 'Login successful',
            token: 'jwt_token_123'
          })
        });
      } else if (url.includes('/api/sessions')) {
        route.fulfill({
          status: 201,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            session_id: 'session_456',
            status: 'active'
          })
        });
      } else {
        route.continue();
      }
    });

    await page.goto('/');
  });

  test.describe('Landing Page and Navigation', () => {
    test('should display main navigation and guru options', async ({ page }) => {
      // Check for main navigation elements
      await expect(page.locator('[data-testid="main-navigation"]')).toBeVisible();
      
      // Check for guru options
      await expect(page.locator('text=Karma Guru')).toBeVisible();
      await expect(page.locator('text=Bhakti Guru')).toBeVisible();
      await expect(page.locator('text=Meditation Guru')).toBeVisible();
      await expect(page.locator('text=Yoga Guru')).toBeVisible();
    });

    test('should handle responsive design', async ({ page }) => {
      // Test mobile viewport
      await page.setViewportSize({ width: 375, height: 667 });
      await expect(page.locator('[data-testid="mobile-menu-toggle"]')).toBeVisible();
      
      // Test tablet viewport
      await page.setViewportSize({ width: 768, height: 1024 });
      
      // Test desktop viewport
      await page.setViewportSize({ width: 1920, height: 1080 });
      await expect(page.locator('[data-testid="desktop-navigation"]')).toBeVisible();
    });

    test('should display hero section with call-to-action', async ({ page }) => {
      await expect(page.locator('[data-testid="hero-section"]')).toBeVisible();
      await expect(page.locator('text=Discover Inner Peace')).toBeVisible();
      await expect(page.locator('[data-testid="get-started-button"]')).toBeVisible();
    });
  });

  test.describe('Guru Chat Functionality', () => {
    test('should enable chat with different guru types', async ({ page }) => {
      // Test Karma Guru
      await page.click('text=Karma Guru');
      await expect(page.locator('[data-testid="chat-interface"]')).toBeVisible();
      
      // Type a message
      await page.fill('[data-testid="chat-input"]', 'What is karma yoga?');
      await page.click('[data-testid="send-button"]');
      
      // Wait for and verify response
      await expect(page.locator('[data-testid="guru-response"]')).toBeVisible();
      await expect(page.locator('text=Thank you for your question about karma yoga')).toBeVisible();
      
      // Test different guru type
      await page.click('[data-testid="change-guru-button"]');
      await page.click('text=Meditation Guru');
      
      await page.fill('[data-testid="chat-input"]', 'How do I start meditating?');
      await page.click('[data-testid="send-button"]');
      
      await expect(page.locator('[data-testid="guru-response"]').last()).toBeVisible();
    });

    test('should handle chat history and context', async ({ page }) => {
      await page.click('text=Spiritual Guru');
      
      // Send first message
      await page.fill('[data-testid="chat-input"]', 'What is dharma?');
      await page.click('[data-testid="send-button"]');
      await expect(page.locator('[data-testid="chat-message-1"]')).toBeVisible();
      
      // Send follow-up message
      await page.fill('[data-testid="chat-input"]', 'Can you explain more?');
      await page.click('[data-testid="send-button"]');
      await expect(page.locator('[data-testid="chat-message-2"]')).toBeVisible();
      
      // Check chat history is preserved
      await expect(page.locator('[data-testid="chat-history"]')).toContainText('What is dharma?');
      await expect(page.locator('[data-testid="chat-history"]')).toContainText('Can you explain more?');
    });

    test('should handle chat errors gracefully', async ({ page }) => {
      // Mock API error
      await page.route('**/api/spiritual/guidance', route => {
        route.fulfill({
          status: 500,
          contentType: 'application/json',
          body: JSON.stringify({
            success: false,
            message: 'Service temporarily unavailable'
          })
        });
      });

      await page.click('text=Spiritual Guru');
      await page.fill('[data-testid="chat-input"]', 'Test message');
      await page.click('[data-testid="send-button"]');
      
      // Should show error message
      await expect(page.locator('[data-testid="error-message"]')).toBeVisible();
      await expect(page.locator('text=Service temporarily unavailable')).toBeVisible();
      
      // Should have retry button
      await expect(page.locator('[data-testid="retry-button"]')).toBeVisible();
    });

    test('should support multilingual chat', async ({ page }) => {
      await page.click('text=Spiritual Guru');
      
      // Change language to Hindi
      await page.click('[data-testid="language-selector"]');
      await page.click('[data-testid="language-option-hi"]');
      
      // Interface should update
      await expect(page.locator('text=आध्यात्मिक गुरु')).toBeVisible();
      
      // Send message in Hindi
      await page.fill('[data-testid="chat-input"]', 'धर्म क्या है?');
      await page.click('[data-testid="send-button"]');
      
      await expect(page.locator('[data-testid="guru-response"]')).toBeVisible();
    });
  });

  test.describe('User Authentication Flow', () => {
    test('should handle complete registration flow', async ({ page }) => {
      // Go to register page
      await page.click('[data-testid="register-link"]');
      await expect(page.locator('[data-testid="registration-form"]')).toBeVisible();
      
      // Fill registration form
      await page.fill('[data-testid="username-input"]', 'testuser');
      await page.fill('[data-testid="email-input"]', 'test@example.com');
      await page.fill('[data-testid="password-input"]', 'testpass123');
      await page.fill('[data-testid="confirm-password-input"]', 'testpass123');
      
      // Accept terms
      await page.check('[data-testid="terms-checkbox"]');
      
      // Submit form
      await page.click('[data-testid="register-button"]');
      
      // Verify successful registration
      await expect(page.locator('[data-testid="success-message"]')).toBeVisible();
      await expect(page.locator('text=Registration successful')).toBeVisible();
    });

    test('should handle login flow', async ({ page }) => {
      await page.click('[data-testid="login-link"]');
      
      // Fill login form
      await page.fill('[data-testid="email-input"]', 'test@example.com');
      await page.fill('[data-testid="password-input"]', 'testpass123');
      await page.click('[data-testid="login-button"]');
      
      // Verify successful login
      await expect(page.locator('[data-testid="user-dashboard"]')).toBeVisible();
      await expect(page.locator('[data-testid="user-menu"]')).toBeVisible();
    });

    test('should handle form validation errors', async ({ page }) => {
      await page.click('[data-testid="register-link"]');
      
      // Submit empty form
      await page.click('[data-testid="register-button"]');
      
      // Check validation errors
      await expect(page.locator('[data-testid="username-error"]')).toBeVisible();
      await expect(page.locator('[data-testid="email-error"]')).toBeVisible();
      await expect(page.locator('[data-testid="password-error"]')).toBeVisible();
      
      // Fill invalid email
      await page.fill('[data-testid="email-input"]', 'invalid-email');
      await page.click('[data-testid="register-button"]');
      await expect(page.locator('text=Please enter a valid email')).toBeVisible();
      
      // Test password mismatch
      await page.fill('[data-testid="password-input"]', 'password1');
      await page.fill('[data-testid="confirm-password-input"]', 'password2');
      await page.click('[data-testid="register-button"]');
      await expect(page.locator('text=Passwords do not match')).toBeVisible();
    });

    test('should handle logout flow', async ({ page }) => {
      // Login first
      await page.click('[data-testid="login-link"]');
      await page.fill('[data-testid="email-input"]', 'test@example.com');
      await page.fill('[data-testid="password-input"]', 'testpass123');
      await page.click('[data-testid="login-button"]');
      
      // Logout
      await page.click('[data-testid="user-menu"]');
      await page.click('[data-testid="logout-button"]');
      
      // Verify logout
      await expect(page.locator('[data-testid="login-link"]')).toBeVisible();
      await expect(page.locator('[data-testid="user-menu"]')).not.toBeVisible();
    });
  });

  test.describe('Meditation Session Tracking', () => {
    test('should track complete meditation session', async ({ page }) => {
      // Login first
      await page.click('[data-testid="login-link"]');
      await page.fill('[data-testid="email-input"]', 'test@example.com');
      await page.fill('[data-testid="password-input"]', 'testpass123');
      await page.click('[data-testid="login-button"]');
      
      // Go to meditation section
      await page.click('[data-testid="meditation-link"]');
      await expect(page.locator('[data-testid="meditation-dashboard"]')).toBeVisible();
      
      // Select meditation type
      await page.click('[data-testid="guided-meditation"]');
      
      // Start session
      await page.click('[data-testid="start-session-button"]');
      await expect(page.locator('[data-testid="session-timer"]')).toBeVisible();
      await expect(page.locator('[data-testid="session-active"]')).toBeVisible();
      
      // Wait for a few seconds (simulate meditation)
      await page.waitForTimeout(5000);
      
      // End session
      await page.click('[data-testid="end-session-button"]');
      
      // Fill session feedback
      await page.selectOption('[data-testid="session-rating"]', '5');
      await page.fill('[data-testid="session-notes"]', 'Very peaceful session');
      await page.click('[data-testid="save-session-button"]');
      
      // Verify session was recorded
      await expect(page.locator('[data-testid="session-completed"]')).toBeVisible();
      await expect(page.locator('text=Session completed successfully')).toBeVisible();
    });

    test('should display session history and statistics', async ({ page }) => {
      // Login and go to meditation dashboard
      await page.click('[data-testid="login-link"]');
      await page.fill('[data-testid="email-input"]', 'test@example.com');
      await page.fill('[data-testid="password-input"]', 'testpass123');
      await page.click('[data-testid="login-button"]');
      await page.click('[data-testid="meditation-link"]');
      
      // Check session history
      await page.click('[data-testid="session-history-tab"]');
      await expect(page.locator('[data-testid="session-list"]')).toBeVisible();
      
      // Check statistics
      await page.click('[data-testid="statistics-tab"]');
      await expect(page.locator('[data-testid="total-sessions"]')).toBeVisible();
      await expect(page.locator('[data-testid="total-duration"]')).toBeVisible();
      await expect(page.locator('[data-testid="average-rating"]')).toBeVisible();
    });

    test('should handle session interruption', async ({ page }) => {
      await page.click('[data-testid="login-link"]');
      await page.fill('[data-testid="email-input"]', 'test@example.com');
      await page.fill('[data-testid="password-input"]', 'testpass123');
      await page.click('[data-testid="login-button"]');
      
      await page.click('[data-testid="meditation-link"]');
      await page.click('[data-testid="guided-meditation"]');
      await page.click('[data-testid="start-session-button"]');
      
      // Navigate away (simulate interruption)
      await page.click('[data-testid="home-link"]');
      
      // Should prompt to save session
      await expect(page.locator('[data-testid="save-session-prompt"]')).toBeVisible();
      
      // Choose to save
      await page.click('[data-testid="save-interrupted-session"]');
      
      // Should save as incomplete session
      await expect(page.locator('[data-testid="session-saved"]')).toBeVisible();
    });
  });

  test.describe('Avatar System Integration', () => {
    test('should display and interact with spiritual avatars', async ({ page }) => {
      // Check avatar display
      await expect(page.locator('[data-testid="avatar-spiritual"]')).toBeVisible();
      await expect(page.locator('[data-testid="avatar-meditation"]')).toBeVisible();
      await expect(page.locator('[data-testid="avatar-karma"]')).toBeVisible();
      
      // Click on avatar should open chat
      await page.click('[data-testid="avatar-spiritual"]');
      await expect(page.locator('[data-testid="chat-interface"]')).toBeVisible();
      await expect(page.locator('[data-testid="avatar-spiritual"]')).toHaveClass(/active/);
    });

    test('should handle avatar customization', async ({ page }) => {
      await page.click('[data-testid="login-link"]');
      await page.fill('[data-testid="email-input"]', 'test@example.com');
      await page.fill('[data-testid="password-input"]', 'testpass123');
      await page.click('[data-testid="login-button"]');
      
      // Go to settings
      await page.click('[data-testid="settings-link"]');
      await page.click('[data-testid="avatar-settings-tab"]');
      
      // Customize avatar
      await page.selectOption('[data-testid="avatar-style"]', 'traditional');
      await page.selectOption('[data-testid="avatar-size"]', 'large');
      await page.click('[data-testid="save-avatar-settings"]');
      
      // Verify changes applied
      await expect(page.locator('[data-testid="settings-saved"]')).toBeVisible();
    });
  });

  test.describe('Scripture Database Integration', () => {
    test('should search and display verses', async ({ page }) => {
      await page.click('[data-testid="scripture-link"]');
      
      // Search for verses
      await page.fill('[data-testid="scripture-search"]', 'dharma');
      await page.click('[data-testid="search-button"]');
      
      // Should display results
      await expect(page.locator('[data-testid="verse-results"]')).toBeVisible();
      await expect(page.locator('[data-testid="verse-item"]').first()).toBeVisible();
      
      // Filter by source
      await page.selectOption('[data-testid="source-filter"]', 'bhagavad-gita');
      await expect(page.locator('[data-testid="filtered-results"]')).toBeVisible();
    });

    test('should display verse details and audio', async ({ page }) => {
      await page.click('[data-testid="scripture-link"]');
      await page.fill('[data-testid="scripture-search"]', 'karma');
      await page.click('[data-testid="search-button"]');
      
      // Click on a verse
      await page.click('[data-testid="verse-item"]').first();
      
      // Should show detailed view
      await expect(page.locator('[data-testid="verse-detail"]')).toBeVisible();
      await expect(page.locator('[data-testid="verse-translation"]')).toBeVisible();
      await expect(page.locator('[data-testid="verse-commentary"]')).toBeVisible();
      
      // Test audio playback
      await expect(page.locator('[data-testid="audio-player"]')).toBeVisible();
      await page.click('[data-testid="play-audio-button"]');
      await expect(page.locator('[data-testid="audio-playing"]')).toBeVisible();
    });
  });

  test.describe('Error Handling and Edge Cases', () => {
    test('should handle network connectivity issues', async ({ page }) => {
      // Simulate offline mode
      await page.context().setOffline(true);
      
      await page.click('text=Spiritual Guru');
      await page.fill('[data-testid="chat-input"]', 'Test message');
      await page.click('[data-testid="send-button"]');
      
      // Should show offline message
      await expect(page.locator('[data-testid="offline-message"]')).toBeVisible();
      
      // Restore connectivity
      await page.context().setOffline(false);
      
      // Should allow retry
      await page.click('[data-testid="retry-button"]');
      await expect(page.locator('[data-testid="connection-restored"]')).toBeVisible();
    });

    test('should handle slow API responses', async ({ page }) => {
      // Mock slow API response
      await page.route('**/api/spiritual/guidance', async route => {
        await new Promise(resolve => setTimeout(resolve, 5000));
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ success: true, response: 'Delayed response' })
        });
      });

      await page.click('text=Spiritual Guru');
      await page.fill('[data-testid="chat-input"]', 'Test message');
      await page.click('[data-testid="send-button"]');
      
      // Should show loading state
      await expect(page.locator('[data-testid="loading-spinner"]')).toBeVisible();
      
      // Should eventually receive response
      await expect(page.locator('text=Delayed response')).toBeVisible({ timeout: 10000 });
    });

    test('should handle invalid user input', async ({ page }) => {
      await page.click('text=Spiritual Guru');
      
      // Test empty message
      await page.click('[data-testid="send-button"]');
      await expect(page.locator('[data-testid="input-validation-error"]')).toBeVisible();
      
      // Test very long message
      const longMessage = 'a'.repeat(5000);
      await page.fill('[data-testid="chat-input"]', longMessage);
      await page.click('[data-testid="send-button"]');
      await expect(page.locator('text=Message too long')).toBeVisible();
      
      // Test special characters
      await page.fill('[data-testid="chat-input"]', '<script>alert("test")</script>');
      await page.click('[data-testid="send-button"]');
      // Should sanitize input properly
      await expect(page.locator('[data-testid="guru-response"]')).toBeVisible();
    });
  });

  test.describe('Performance and Accessibility', () => {
    test('should meet accessibility standards', async ({ page }) => {
      // Check for proper heading structure
      await expect(page.locator('h1')).toBeVisible();
      
      // Check for alt text on images
      const images = await page.locator('img').all();
      for (const img of images) {
        await expect(img).toHaveAttribute('alt');
      }
      
      // Check for proper form labels
      const inputs = await page.locator('input').all();
      for (const input of inputs) {
        const id = await input.getAttribute('id');
        if (id) {
          await expect(page.locator(`label[for="${id}"]`)).toBeVisible();
        }
      }
      
      // Check keyboard navigation
      await page.keyboard.press('Tab');
      await expect(page.locator(':focus')).toBeVisible();
    });

    test('should load efficiently', async ({ page }) => {
      const startTime = Date.now();
      await page.goto('/');
      const loadTime = Date.now() - startTime;
      
      // Should load within reasonable time
      expect(loadTime).toBeLessThan(5000);
      
      // Check for critical elements
      await expect(page.locator('[data-testid="main-navigation"]')).toBeVisible();
      await expect(page.locator('[data-testid="hero-section"]')).toBeVisible();
    });
  });
});
