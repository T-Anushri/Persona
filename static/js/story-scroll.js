// Story Scroll - Swipeable Interface for Artisan Stories
class StoryScroll {
    constructor() {
        this.currentStoryIndex = 0;
        this.stories = [];
        this.isScrolling = false;
        this.touchStartY = 0;
        this.touchEndY = 0;
        this.autoScrollTimer = null;
        this.filters = {
            craft: 'all',
            era: 'all',
            tone: 'all'
        };
        
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.init());
        } else {
            this.init();
        }
    }
    
    init() {
        // Check if we're on the marketplace page
        if (!document.querySelector('.story-scroll-container')) {
            console.log('Story scroll container not found, skipping initialization');
            return;
        }
        
        this.loadStories();
        this.setupEventListeners();
        this.setupFilters();
        
        // Only start auto-scroll if we have stories
        if (this.stories.length > 0) {
            this.startAutoScroll();
        }
    }
    
    loadStories() {
        // Get stories from DOM instead of mock data
        const storyCards = document.querySelectorAll('.story-card');
        this.stories = [];
        
        if (storyCards.length === 0) {
            console.warn('No story cards found in DOM');
            return;
        }
        
        storyCards.forEach((card, index) => {
            const artisanName = card.querySelector('.artisan-name')?.textContent || 'Unknown Artisan';
            const artisanCraft = card.querySelector('.artisan-craft')?.textContent || 'Craftsperson';
            const storyTitle = card.querySelector('.story-title')?.textContent || 'Artisan Story';
            const storyText = card.querySelector('.story-text')?.textContent || '';
            
            this.stories.push({
                id: index + 1,
                element: card,
                artisan: {
                    name: artisanName,
                    craft: artisanCraft
                },
                story: {
                    title: storyTitle,
                    content: storyText
                }
            });
        });
        
        console.log(`Loaded ${this.stories.length} stories from DOM`);
        
        this.renderStories();
    }
    
    renderStories() {
        // Stories are already rendered by Flask template
        // Just ensure the first one is active
        if (this.stories.length > 0) {
            this.showStory(0);
        }
    }
    
    setupEventListeners() {
        const container = document.querySelector('.story-scroll-container');
        
        // Touch events for mobile swiping
        container.addEventListener('touchstart', (e) => {
            this.touchStartY = e.touches[0].clientY;
            this.stopAutoScroll();
        });
        
        container.addEventListener('touchend', (e) => {
            this.touchEndY = e.changedTouches[0].clientY;
            this.handleSwipe();
            this.startAutoScroll();
        });
        
        // Mouse wheel for desktop
        container.addEventListener('wheel', (e) => {
            e.preventDefault();
            this.stopAutoScroll();
            
            if (e.deltaY > 0) {
                this.nextStory();
            } else {
                this.previousStory();
            }
            
            setTimeout(() => this.startAutoScroll(), 3000);
        });
        
        // Keyboard navigation
        document.addEventListener('keydown', (e) => {
            if (document.querySelector('.story-scroll-view').classList.contains('active')) {
                if (e.key === 'ArrowDown' || e.key === ' ') {
                    e.preventDefault();
                    this.nextStory();
                } else if (e.key === 'ArrowUp') {
                    e.preventDefault();
                    this.previousStory();
                }
            }
        });
        
        // Story interactions
        container.addEventListener('click', (e) => {
            if (e.target.classList.contains('like-btn')) {
                e.preventDefault();
                this.toggleLike(e.target);
            } else if (e.target.classList.contains('follow-btn')) {
                e.preventDefault();
                this.toggleFollow(e.target);
            } else if (e.target.classList.contains('share-btn')) {
                e.preventDefault();
                this.shareStory(e.target);
            } else if (e.target.classList.contains('add-to-bundle-btn')) {
                e.preventDefault();
                this.addToBundle(e.target);
            } else if (e.target.classList.contains('chat-btn')) {
                e.preventDefault();
                this.startChat(e.target);
            } else if (e.target.classList.contains('view-profile-btn')) {
                e.preventDefault();
                this.viewProfile(e.target);
            }
        });
        
        // Pause auto-scroll on hover
        container.addEventListener('mouseenter', () => this.stopAutoScroll());
        container.addEventListener('mouseleave', () => this.startAutoScroll());
    }
    
    setupFilters() {
        const filterButtons = document.querySelectorAll('.story-filter-btn');
        
        filterButtons.forEach((button) => {
            button.addEventListener('click', (e) => {
                const filterType = button.dataset.filter;
                const filterValue = button.dataset.value;
                
                this.filters[filterType] = filterValue;
                this.applyFilters();
                
                // Update active filter button
                filterButtons.forEach((btn) => btn.classList.remove('active'));
                button.classList.add('active');
            });
        });
    }
    
    applyFilters() {
        let filteredStories = this.stories;
        
        if (this.filters.craft !== 'all') {
            filteredStories = filteredStories.filter(story => 
                story.artisan.craft.toLowerCase() === this.filters.craft.toLowerCase()
            );
        }
        
        if (this.filters.era !== 'all') {
            filteredStories = filteredStories.filter(story => 
                story.story.era === this.filters.era
            );
        }
        
        if (this.filters.tone !== 'all') {
            filteredStories = filteredStories.filter(story => 
                story.story.tone === this.filters.tone
            );
        }
        
        this.stories = filteredStories;
        this.currentStoryIndex = 0;
        this.renderStories();
    }
    
    handleSwipe() {
        const swipeThreshold = 50;
        const swipeDistance = this.touchStartY - this.touchEndY;
        
        if (Math.abs(swipeDistance) > swipeThreshold) {
            if (swipeDistance > 0) {
                // Swipe up - next story
                this.nextStory();
            } else {
                // Swipe down - previous story
                this.previousStory();
            }
        }
    }
    
    nextStory() {
        if (this.isScrolling) return;
        
        this.isScrolling = true;
        this.currentStoryIndex = (this.currentStoryIndex + 1) % this.stories.length;
        this.showStory(this.currentStoryIndex);
        
        setTimeout(() => {
            this.isScrolling = false;
        }, 500);
    }
    
    previousStory() {
        if (this.isScrolling) return;
        
        this.isScrolling = true;
        this.currentStoryIndex = this.currentStoryIndex === 0 ? 
            this.stories.length - 1 : this.currentStoryIndex - 1;
        this.showStory(this.currentStoryIndex);
        
        setTimeout(() => {
            this.isScrolling = false;
        }, 500);
    }
    
    showStory(index) {
        const story = this.stories[index];
        const container = document.querySelector('.story-scroll-container');
        
        // Hide all stories
        container.querySelectorAll('.story-card').forEach((card) => card.classList.remove('active'));
        
        // Show the current story
        story.element.classList.add('active');
        
        // Update progress indicator
        this.updateProgressIndicator();
    }
    
    updateProgressIndicator() {
        const progress = ((this.currentStoryIndex + 1) / this.stories.length) * 100;
        document.querySelector('.story-progress-bar').style.width = `${progress}%`;
        document.querySelector('.story-counter').textContent = `${this.currentStoryIndex + 1} / ${this.stories.length}`;
    }
    
    startAutoScroll() {
        this.stopAutoScroll();
        this.autoScrollTimer = setInterval(() => {
            this.nextStory();
        }, 8000); // Auto-advance every 8 seconds
    }
    
    stopAutoScroll() {
        if (this.autoScrollTimer) {
            clearInterval(this.autoScrollTimer);
            this.autoScrollTimer = null;
        }
    }
    
    toggleLike(button) {
        const storyId = button.dataset.storyId;
        const icon = button.querySelector('i');
        const countSpan = button.parentNode.querySelector('.stat-count');
        let count = parseInt(countSpan.textContent);
        
        if (icon.classList.contains('far')) {
            // Like the story
            icon.classList.replace('far', 'fas');
            button.classList.add('liked');
            count++;
            
            // Add animation
            button.classList.add('pulse-animation');
            setTimeout(() => button.classList.remove('pulse-animation'), 600);
            
            this.showAlert('Story liked! ❤️', 'success');
        } else {
            // Unlike the story
            icon.classList.replace('fas', 'far');
            button.classList.remove('liked');
            count--;
        }
        
        countSpan.textContent = count;
        
        // Send to backend
        this.updateStoryLike(storyId, icon.classList.contains('fas'));
    }
    
    toggleFollow(button) {
        const artisanId = button.dataset.artisanId;
        const icon = button.querySelector('i');
        
        if (icon.classList.contains('fa-user-plus')) {
            icon.classList.replace('fa-user-plus', 'fa-user-check');
            button.classList.add('following');
            this.showAlert('Now following artisan! 👥', 'success');
        } else {
            icon.classList.replace('fa-user-check', 'fa-user-plus');
            button.classList.remove('following');
            this.showAlert('Unfollowed artisan', 'info');
        }
        
        // Send to backend
        this.updateArtisanFollow(artisanId, icon.classList.contains('fa-user-check'));
    }
    
    shareStory(button) {
        const storyId = button.dataset.storyId;
        const story = this.stories.find(s => s.id === parseInt(storyId));
        
        if (navigator.share) {
            navigator.share({
                title: story.story.title,
                text: story.story.content,
                url: window.location.href + `?story=${storyId}`
            });
        } else {
            // Fallback - copy to clipboard
            const shareUrl = window.location.href + `?story=${storyId}`;
            navigator.clipboard.writeText(shareUrl).then(() => {
                this.showAlert('Story link copied to clipboard! 📋', 'success');
            });
        }
    }
    
    addToBundle(button) {
        const productId = button.closest('.product-card-mini').dataset.productId;
        const product = this.findProductById(productId);
        
        if (product) {
            // Add visual feedback
            button.textContent = 'Added!';
            button.classList.add('btn-success');
            
            setTimeout(() => {
                button.textContent = 'Add to Bundle';
                button.classList.remove('btn-success');
            }, 2000);
            
            this.showAlert(`${product.name} added to bundle! 🛍️`, 'success');
            
            // Send to backend
            this.addProductToBundle(productId);
        }
    }
    
    startChat(button) {
        const artisanId = button.dataset.artisanId;
        const artisan = this.stories.find(s => s.id === parseInt(artisanId))?.artisan;
        
        if (artisan) {
            this.showAlert(`Starting chat with ${artisan.name}... 💬`, 'info');
            
            // In a real app, this would open a chat interface
            setTimeout(() => {
                window.location.href = `/chat/${artisanId}`;
            }, 1000);
        }
    }
    
    viewProfile(button) {
        const artisanId = button.dataset.artisanId;
        window.location.href = `/artisan/${artisanId}`;
    }
    
    findProductById(productId) {
        for (const story of this.stories) {
            const product = story.products.find(p => p.id === parseInt(productId));
            if (product) return product;
        }
        return null;
    }
    
    updateStoryLike(storyId, isLiked) {
        fetch('/api/story/like', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                story_id: storyId,
                liked: isLiked
            })
        })
        .catch((error) => console.error('Failed to update story like:', error));
    }
    
    updateArtisanFollow(artisanId, isFollowing) {
        fetch('/api/artisan/follow', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                artisan_id: artisanId,
                following: isFollowing
            })
        })
        .catch((error) => console.error('Failed to update artisan follow:', error));
    }
    
    addProductToBundle(productId) {
        fetch('/api/bundle/add', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                product_id: productId
            })
        })
        .catch((error) => console.error('Failed to add product to bundle:', error));
    }
    
    showAlert(message, type = 'info') {
        if (window.PersonaApp && window.PersonaApp.showAlert) {
            window.PersonaApp.showAlert(message, type);
        } else {
            console.log(`${type.toUpperCase()}: ${message}`);
        }
    }
}

// Initialize Story Scroll when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    if (document.querySelector('.story-scroll-container')) {
        window.storyScroll = new StoryScroll();
    }
});

// Export for use in other scripts
window.StoryScroll = StoryScroll;
