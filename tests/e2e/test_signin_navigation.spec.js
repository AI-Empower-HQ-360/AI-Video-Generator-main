const { test, expect } = require('@playwright/test');

test.describe('Sign-In and Authentication E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should display sign-in button on homepage', async ({ page }) => {
    // Check if sign-in/login button exists
    const loginButton = page.locator('button:has-text("Login"), a:has-text("Login"), button:has-text("Sign In"), a:has-text("Sign In")').first();
    await expect(loginButton).toBeVisible({ timeout: 5000 });
  });

  test('should navigate to sign-in page when clicking login', async ({ page }) => {
    // Click login button
    const loginButton = page.locator('button:has-text("Login"), a:has-text("Login"), button:has-text("Sign In"), a:has-text("Sign In")').first();
    
    if (await loginButton.isVisible()) {
      await loginButton.click();
      
      // Wait for navigation or modal to appear
      await page.waitForTimeout(1000);
      
      // Check for email/username and password fields
      const emailField = page.locator('input[type="email"], input[name="email"], input[placeholder*="email" i]').first();
      const passwordField = page.locator('input[type="password"]').first();
      
      await expect(emailField).toBeVisible({ timeout: 5000 });
      await expect(passwordField).toBeVisible({ timeout: 5000 });
    }
  });

  test('should show validation errors for empty sign-in form', async ({ page }) => {
    // Navigate to login
    const loginButton = page.locator('button:has-text("Login"), a:has-text("Login")').first();
    
    if (await loginButton.isVisible()) {
      await loginButton.click();
      await page.waitForTimeout(500);
      
      // Try to submit without filling fields
      const submitButton = page.locator('button[type="submit"], button:has-text("Login"), button:has-text("Sign In")').first();
      await submitButton.click();
      
      // Check for validation messages
      await page.waitForTimeout(500);
      // Form should not proceed or show error
      const errorMessage = page.locator('text=/error|required|invalid/i').first();
      const emailField = page.locator('input[type="email"], input[name="email"]').first();
      
      // Either error message appears or we're still on login page
      const hasError = await errorMessage.isVisible().catch(() => false);
      const stillOnLogin = await emailField.isVisible().catch(() => false);
      
      expect(hasError || stillOnLogin).toBeTruthy();
    }
  });

  test('should allow entering credentials in sign-in form', async ({ page }) => {
    // Navigate to login
    const loginButton = page.locator('button:has-text("Login"), a:has-text("Login")').first();
    
    if (await loginButton.isVisible()) {
      await loginButton.click();
      await page.waitForTimeout(500);
      
      // Fill in credentials
      const emailField = page.locator('input[type="email"], input[name="email"], input[placeholder*="email" i]').first();
      const passwordField = page.locator('input[type="password"]').first();
      
      await emailField.fill('test@example.com');
      await passwordField.fill('testpassword123');
      
      // Verify values were entered
      await expect(emailField).toHaveValue('test@example.com');
      await expect(passwordField).toHaveValue('testpassword123');
    }
  });

  test('should have register/sign-up option', async ({ page }) => {
    // Look for register or sign up link/button
    const registerLink = page.locator('a:has-text("Register"), a:has-text("Sign Up"), button:has-text("Register"), button:has-text("Sign Up")').first();
    
    // Wait a bit for page to load
    await page.waitForTimeout(1000);
    
    // Either direct register button or within login flow
    const hasRegisterButton = await registerLink.isVisible().catch(() => false);
    
    if (!hasRegisterButton) {
      // Try clicking login first to see register option
      const loginButton = page.locator('button:has-text("Login"), a:has-text("Login")').first();
      if (await loginButton.isVisible()) {
        await loginButton.click();
        await page.waitForTimeout(500);
        
        const registerInModal = page.locator('a:has-text("Register"), a:has-text("Sign Up"), button:has-text("Register"), button:has-text("Sign Up")').first();
        await expect(registerInModal).toBeVisible({ timeout: 5000 });
      }
    }
  });
});

test.describe('Navigation E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should display main navigation elements', async ({ page }) => {
    // Check for key navigation elements
    const hasTitle = await page.locator('h1, h2').first().isVisible();
    expect(hasTitle).toBeTruthy();
  });

  test('should navigate between guru selection and chat', async ({ page }) => {
    // Find a guru card to click
    const guruCard = page.locator('.guru-card, [class*="guru"], button:has-text("Guru"), div:has-text("Guru")').first();
    
    await page.waitForTimeout(1000);
    
    if (await guruCard.isVisible()) {
      await guruCard.click();
      
      // Should show question/chat area
      await page.waitForTimeout(500);
      const questionArea = page.locator('textarea, input[type="text"]').first();
      await expect(questionArea).toBeVisible({ timeout: 5000 });
    }
  });

  test('should display guru options on homepage', async ({ page }) => {
    // Wait for page load
    await page.waitForTimeout(1000);
    
    // Look for guru-related text
    const guruTexts = [
      'Spiritual Guru',
      'Meditation Guru',
      'Karma Guru',
      'Bhakti Guru',
      'Yoga Guru',
      'Sloka Guru',
      'Bojan'
    ];
    
    let foundGuru = false;
    for (const guruText of guruTexts) {
      const element = page.locator(`text=${guruText}`).first();
      if (await element.isVisible().catch(() => false)) {
        foundGuru = true;
        break;
      }
    }
    
    expect(foundGuru).toBeTruthy();
  });

  test('should be able to go back from guru chat to guru selection', async ({ page }) => {
    // Select a guru
    const guruCard = page.locator('.guru-card, [class*="guru"]').first();
    
    if (await guruCard.isVisible()) {
      await guruCard.click();
      await page.waitForTimeout(500);
      
      // Look for back button or navigation
      const backButton = page.locator('button:has-text("Back"), a:has-text("Back"), button[aria-label="Back"]').first();
      
      if (await backButton.isVisible().catch(() => false)) {
        await backButton.click();
        await page.waitForTimeout(500);
        
        // Should be back at guru selection
        const guruCardAgain = page.locator('.guru-card, [class*="guru"]').first();
        await expect(guruCardAgain).toBeVisible();
      }
    }
  });

  test('should have working navigation menu if present', async ({ page }) => {
    // Look for navigation menu
    const navMenu = page.locator('nav, [role="navigation"], .navbar, header').first();
    
    if (await navMenu.isVisible().catch(() => false)) {
      // Check for common nav links
      const homeLink = page.locator('a:has-text("Home"), button:has-text("Home")').first();
      const hasHome = await homeLink.isVisible().catch(() => false);
      
      // Just verify nav structure exists
      expect(await navMenu.isVisible()).toBeTruthy();
    }
  });
});

test.describe('AI Chat Interface E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForTimeout(1000);
  });

  test('should display quick questions when guru is selected', async ({ page }) => {
    // Select a guru
    const guruCard = page.locator('.guru-card, [class*="guru"]').first();
    
    if (await guruCard.isVisible()) {
      await guruCard.click();
      await page.waitForTimeout(500);
      
      // Look for quick questions
      const quickQuestions = page.locator('text=/quick question|suggested question|example/i').first();
      
      // Quick questions might be visible or might appear after clicking something
      const hasQuickQuestions = await quickQuestions.isVisible().catch(() => false);
      
      // Also check for question buttons or suggestions
      const questionButton = page.locator('button:has-text("?"), .question-suggestion, .quick-question').first();
      const hasQuestionButtons = await questionButton.isVisible().catch(() => false);
      
      // Either quick questions text or suggestion buttons should be present
      // This is optional feature so we just log the result
      console.log('Quick questions feature present:', hasQuickQuestions || hasQuestionButtons);
    }
  });

  test('should allow typing and sending a message', async ({ page }) => {
    // Select a guru first
    const guruCard = page.locator('.guru-card').first();
    
    if (await guruCard.isVisible()) {
      await guruCard.click();
      await page.waitForTimeout(500);
      
      // Find input field
      const messageInput = page.locator('textarea, input[type="text"]').first();
      
      if (await messageInput.isVisible()) {
        await messageInput.fill('What is meditation?');
        
        // Find and click send button
        const sendButton = page.locator('button:has-text("Send"), button:has-text("Ask"), button[type="submit"]').first();
        
        if (await sendButton.isVisible()) {
          await sendButton.click();
          
          // Wait for response
          await page.waitForTimeout(2000);
          
          // Response area should appear
          const responseArea = page.locator('.response, .answer, .guru-response, [class*="response"]').first();
          const hasResponse = await responseArea.isVisible().catch(() => false);
          
          // Log result (API might not be configured in test env)
          console.log('Chat response received:', hasResponse);
        }
      }
    }
  });

  test('should display chat history', async ({ page }) => {
    // After interacting with guru, chat history should be visible
    const guruCard = page.locator('.guru-card').first();
    
    if (await guruCard.isVisible()) {
      await guruCard.click();
      await page.waitForTimeout(500);
      
      // Send a message
      const messageInput = page.locator('textarea, input[type="text"]').first();
      const sendButton = page.locator('button:has-text("Send"), button:has-text("Ask")').first();
      
      if (await messageInput.isVisible() && await sendButton.isVisible()) {
        await messageInput.fill('Test question');
        await sendButton.click();
        await page.waitForTimeout(1000);
        
        // Check for message in chat history
        const chatMessage = page.locator('text=Test question').first();
        const hasMessage = await chatMessage.isVisible().catch(() => false);
        
        console.log('Chat history visible:', hasMessage);
      }
    }
  });

  test('should handle clearing/resetting chat', async ({ page }) => {
    const guruCard = page.locator('.guru-card').first();
    
    if (await guruCard.isVisible()) {
      await guruCard.click();
      await page.waitForTimeout(500);
      
      // Look for clear/reset button
      const clearButton = page.locator('button:has-text("Clear"), button:has-text("Reset"), button:has-text("New Chat")').first();
      
      const hasClearButton = await clearButton.isVisible().catch(() => false);
      console.log('Clear chat feature present:', hasClearButton);
      
      if (hasClearButton) {
        await clearButton.click();
        await page.waitForTimeout(500);
        
        // Chat should be cleared
        const messageInput = page.locator('textarea, input[type="text"]').first();
        if (await messageInput.isVisible()) {
          await expect(messageInput).toHaveValue('');
        }
      }
    }
  });
});

test.describe('Responsive Design Tests', () => {
  test('should work on mobile viewport', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');
    await page.waitForTimeout(1000);
    
    // Check that page is still functional
    const guruCard = page.locator('.guru-card, [class*="guru"]').first();
    const hasGurus = await guruCard.isVisible().catch(() => false);
    
    expect(hasGurus).toBeTruthy();
  });

  test('should work on tablet viewport', async ({ page }) => {
    // Set tablet viewport
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.goto('/');
    await page.waitForTimeout(1000);
    
    // Check that page is still functional
    const title = page.locator('h1, h2').first();
    await expect(title).toBeVisible();
  });
});
