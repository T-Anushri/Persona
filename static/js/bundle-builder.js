// Bundle Builder Canvas - AI-Suggested Product Combinations
class BundleBuilder {
    constructor() {
        this.selectedProducts = [];
        this.suggestedBundles = [];
        this.currentBundle = {
            id: null,
            name: '',
            products: [],
            totalPrice: 0,
            discountPercentage: 0,
            finalPrice: 0,
            theme: '',
            occasion: ''
        };
        this.aiSuggestions = [];
        this.draggedProduct = null;
        
        this.init();
    }
    
    init() {
        this.loadAvailableProducts();
        this.setupEventListeners();
        this.setupDragAndDrop();
        this.generateAISuggestions();
        this.updateBundleDisplay();
    }
    
    loadAvailableProducts() {
        // Mock product data - in real app, load from backend
        this.availableProducts = [
            {
                id: 101,
                name: "Handcrafted Water Pot",
                price: 1200,
                category: "pottery",
                artisan: "Priya Sharma",
                image: "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=300&h=300&fit=crop",
                tags: ["traditional", "functional", "ceramic"],
                compatibility: ["pottery", "textiles", "woodwork"]
            },
            {
                id: 102,
                name: "Decorative Vase Set",
                price: 2500,
                category: "pottery",
                artisan: "Priya Sharma",
                image: "https://images.unsplash.com/photo-1610701596007-11502861dcfa?w=300&h=300&fit=crop",
                tags: ["decorative", "ceramic", "set"],
                compatibility: ["pottery", "textiles"]
            },
            {
                id: 201,
                name: "Carved Wooden Box",
                price: 3500,
                category: "woodwork",
                artisan: "Ravi Kumar",
                image: "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=300&h=300&fit=crop",
                tags: ["storage", "carved", "teak"],
                compatibility: ["woodwork", "textiles", "jewelry"]
            },
            {
                id: 301,
                name: "Embroidered Dupatta",
                price: 1800,
                category: "textiles",
                artisan: "Meera Devi",
                image: "https://images.unsplash.com/photo-1610030469983-98e550d6193c?w=300&h=300&fit=crop",
                tags: ["clothing", "embroidered", "silk"],
                compatibility: ["textiles", "jewelry"]
            },
            {
                id: 401,
                name: "Silver Bangles Set",
                price: 4200,
                category: "jewelry",
                artisan: "Lakshmi Bai",
                image: "https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=300&h=300&fit=crop",
                tags: ["silver", "traditional", "set"],
                compatibility: ["jewelry", "textiles"]
            },
            {
                id: 501,
                name: "Brass Lamp",
                price: 2800,
                category: "metalwork",
                artisan: "Suresh Patel",
                image: "https://images.unsplash.com/photo-1513475382585-d06e58bcb0e0?w=300&h=300&fit=crop",
                tags: ["brass", "lighting", "traditional"],
                compatibility: ["metalwork", "pottery", "woodwork"]
            }
        ];
        
        this.renderProductGrid();
    }
    
    renderProductGrid() {
        const grid = $('.products-grid');
        if (!grid.length) return;
        
        grid.empty();
        
        this.availableProducts.forEach(product => {
            const productCard = this.createProductCard(product);
            grid.append(productCard);
        });
    }
    
    createProductCard(product) {
        const isSelected = this.currentBundle.products.some(p => p.id === product.id);
        
        return $(`
            <div class="product-card ${isSelected ? 'selected' : ''}" 
                 data-product-id="${product.id}" 
                 draggable="true">
                <div class="product-image-container">
                    <img src="${product.image}" alt="${product.name}" class="product-image">
                    <div class="product-overlay">
                        <button class="btn btn-sm btn-primary add-to-bundle-btn">
                            <i class="fas fa-plus"></i>
                        </button>
                    </div>
                </div>
                <div class="product-info">
                    <h6 class="product-name">${product.name}</h6>
                    <p class="product-artisan">by ${product.artisan}</p>
                    <p class="product-price">₹${product.price.toLocaleString()}</p>
                    <div class="product-tags">
                        ${product.tags.slice(0, 2).map(tag => 
                            `<span class="tag">${tag}</span>`
                        ).join('')}
                    </div>
                </div>
            </div>
        `);
    }
    
    setupEventListeners() {
        // Add product to bundle
        $(document).on('click', '.add-to-bundle-btn', (e) => {
            e.preventDefault();
            e.stopPropagation();
            const productId = parseInt($(e.target).closest('.product-card').data('product-id'));
            this.addProductToBundle(productId);
        });
        
        // Remove product from bundle
        $(document).on('click', '.remove-from-bundle-btn', (e) => {
            e.preventDefault();
            const productId = parseInt($(e.target).closest('.bundle-product').data('product-id'));
            this.removeProductFromBundle(productId);
        });
        
        // Bundle theme selection
        $('.theme-btn').on('click', (e) => {
            const theme = $(e.target).data('theme');
            this.selectTheme(theme);
        });
        
        // Bundle occasion selection
        $('.occasion-btn').on('click', (e) => {
            const occasion = $(e.target).data('occasion');
            this.selectOccasion(occasion);
        });
        
        // AI suggestion actions
        $(document).on('click', '.apply-suggestion-btn', (e) => {
            const suggestionIndex = parseInt($(e.target).data('suggestion-index'));
            this.applySuggestion(suggestionIndex);
        });
        
        // Save bundle
        $('.save-bundle-btn').on('click', () => {
            this.saveBundle();
        });
        
        // Clear bundle
        $('.clear-bundle-btn').on('click', () => {
            this.clearBundle();
        });
        
        // Bundle name input
        $('#bundleName').on('input', (e) => {
            this.currentBundle.name = $(e.target).val();
            this.updateBundleDisplay();
        });
        
        // Generate new suggestions
        $('.refresh-suggestions-btn').on('click', () => {
            this.generateAISuggestions();
        });
    }
    
    setupDragAndDrop() {
        // Product drag start
        $(document).on('dragstart', '.product-card', (e) => {
            const productId = parseInt($(e.target).data('product-id'));
            this.draggedProduct = this.availableProducts.find(p => p.id === productId);
            e.originalEvent.dataTransfer.effectAllowed = 'copy';
        });
        
        // Bundle canvas drop zone
        $('.bundle-canvas').on('dragover', (e) => {
            e.preventDefault();
            e.originalEvent.dataTransfer.dropEffect = 'copy';
            $('.bundle-canvas').addClass('drag-over');
        });
        
        $('.bundle-canvas').on('dragleave', () => {
            $('.bundle-canvas').removeClass('drag-over');
        });
        
        $('.bundle-canvas').on('drop', (e) => {
            e.preventDefault();
            $('.bundle-canvas').removeClass('drag-over');
            
            if (this.draggedProduct) {
                this.addProductToBundle(this.draggedProduct.id);
                this.draggedProduct = null;
            }
        });
    }
    
    addProductToBundle(productId) {
        const product = this.availableProducts.find(p => p.id === productId);
        if (!product) return;
        
        // Check if already in bundle
        if (this.currentBundle.products.some(p => p.id === productId)) {
            this.showAlert('Product already in bundle', 'warning');
            return;
        }
        
        // Add to bundle
        this.currentBundle.products.push(product);
        this.calculateBundlePrice();
        this.updateBundleDisplay();
        this.renderProductGrid(); // Update selection state
        this.generateAISuggestions(); // Refresh suggestions
        
        // Visual feedback
        this.showAlert(`${product.name} added to bundle!`, 'success');
        
        // Animate the addition
        this.animateProductAddition(product);
    }
    
    removeProductFromBundle(productId) {
        this.currentBundle.products = this.currentBundle.products.filter(p => p.id !== productId);
        this.calculateBundlePrice();
        this.updateBundleDisplay();
        this.renderProductGrid(); // Update selection state
        this.generateAISuggestions(); // Refresh suggestions
        
        const product = this.availableProducts.find(p => p.id === productId);
        this.showAlert(`${product.name} removed from bundle`, 'info');
    }
    
    calculateBundlePrice() {
        this.currentBundle.totalPrice = this.currentBundle.products.reduce((sum, product) => sum + product.price, 0);
        
        // Calculate discount based on bundle size and compatibility
        let discount = 0;
        const productCount = this.currentBundle.products.length;
        
        if (productCount >= 2) discount += 5; // 5% for 2+ items
        if (productCount >= 3) discount += 5; // Additional 5% for 3+ items
        if (productCount >= 5) discount += 10; // Additional 10% for 5+ items
        
        // Compatibility bonus
        const categories = [...new Set(this.currentBundle.products.map(p => p.category))];
        if (categories.length >= 2) discount += 5; // 5% for cross-category bundles
        
        // Theme/occasion bonus
        if (this.currentBundle.theme) discount += 3;
        if (this.currentBundle.occasion) discount += 3;
        
        this.currentBundle.discountPercentage = Math.min(discount, 30); // Max 30% discount
        this.currentBundle.finalPrice = this.currentBundle.totalPrice * (1 - this.currentBundle.discountPercentage / 100);
    }
    
    updateBundleDisplay() {
        // Update bundle summary
        $('.bundle-item-count').text(this.currentBundle.products.length);
        $('.bundle-total-price').text(`₹${this.currentBundle.totalPrice.toLocaleString()}`);
        $('.bundle-discount').text(`${this.currentBundle.discountPercentage}%`);
        $('.bundle-final-price').text(`₹${Math.round(this.currentBundle.finalPrice).toLocaleString()}`);
        $('.bundle-savings').text(`₹${Math.round(this.currentBundle.totalPrice - this.currentBundle.finalPrice).toLocaleString()}`);
        
        // Update bundle products display
        const bundleProducts = $('.bundle-products');
        bundleProducts.empty();
        
        this.currentBundle.products.forEach(product => {
            const productElement = $(`
                <div class="bundle-product" data-product-id="${product.id}">
                    <img src="${product.image}" alt="${product.name}" class="bundle-product-image">
                    <div class="bundle-product-info">
                        <h6 class="bundle-product-name">${product.name}</h6>
                        <p class="bundle-product-price">₹${product.price.toLocaleString()}</p>
                    </div>
                    <button class="btn btn-sm btn-outline-danger remove-from-bundle-btn">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            `);
            bundleProducts.append(productElement);
        });
        
        // Update save button state
        $('.save-bundle-btn').prop('disabled', this.currentBundle.products.length === 0);
    }
    
    generateAISuggestions() {
        // AI-powered suggestions based on current bundle
        this.aiSuggestions = [];
        
        if (this.currentBundle.products.length === 0) {
            // Suggest popular starter bundles
            this.aiSuggestions = [
                {
                    title: "Traditional Home Decor",
                    description: "Perfect for decorating your living space with authentic crafts",
                    products: [101, 102, 501], // Water pot, vase set, brass lamp
                    reason: "These items complement each other beautifully and create a cohesive traditional aesthetic",
                    confidence: 0.92
                },
                {
                    title: "Wedding Gift Collection",
                    description: "Thoughtful gifts for newlyweds",
                    products: [201, 301, 401], // Wooden box, dupatta, bangles
                    reason: "Traditional wedding essentials that represent good fortune and prosperity",
                    confidence: 0.88
                },
                {
                    title: "Artisan Sampler",
                    description: "Experience crafts from different regions",
                    products: [101, 201, 301], // One from each major artisan
                    reason: "Diverse collection showcasing various traditional Indian crafts",
                    confidence: 0.85
                }
            ];
        } else {
            // Suggest complementary products
            const currentCategories = this.currentBundle.products.map(p => p.category);
            const availableProducts = this.availableProducts.filter(p => 
                !this.currentBundle.products.some(bp => bp.id === p.id)
            );
            
            // Find compatible products
            const compatibleProducts = availableProducts.filter(product => {
                return this.currentBundle.products.some(bundleProduct => 
                    bundleProduct.compatibility.includes(product.category) ||
                    product.compatibility.includes(bundleProduct.category)
                );
            });
            
            if (compatibleProducts.length > 0) {
                // Create suggestions based on themes
                const themes = ['traditional', 'modern', 'festive', 'minimalist'];
                
                themes.forEach(theme => {
                    const themeProducts = compatibleProducts.filter(p => 
                        p.tags.includes(theme) || this.getThemeCompatibility(p, theme) > 0.7
                    ).slice(0, 2);
                    
                    if (themeProducts.length > 0) {
                        this.aiSuggestions.push({
                            title: `${theme.charAt(0).toUpperCase() + theme.slice(1)} Enhancement`,
                            description: `Add ${theme} elements to your bundle`,
                            products: themeProducts.map(p => p.id),
                            reason: `These items enhance the ${theme} aesthetic of your current selection`,
                            confidence: 0.75 + (themeProducts.length * 0.1)
                        });
                    }
                });
            }
            
            // Price-based suggestions
            const budgetRemaining = 10000 - this.currentBundle.totalPrice; // Assume 10k budget
            if (budgetRemaining > 0) {
                const affordableProducts = availableProducts.filter(p => p.price <= budgetRemaining);
                if (affordableProducts.length > 0) {
                    const bestValue = affordableProducts.sort((a, b) => b.price - a.price).slice(0, 2);
                    this.aiSuggestions.push({
                        title: "Best Value Addition",
                        description: "Maximize your bundle value within budget",
                        products: bestValue.map(p => p.id),
                        reason: "These items offer the best value for your remaining budget",
                        confidence: 0.80
                    });
                }
            }
        }
        
        this.renderAISuggestions();
    }
    
    getThemeCompatibility(product, theme) {
        const themeKeywords = {
            traditional: ['traditional', 'heritage', 'classic', 'ethnic'],
            modern: ['modern', 'contemporary', 'sleek', 'minimalist'],
            festive: ['festive', 'celebration', 'decorative', 'ornate'],
            minimalist: ['simple', 'clean', 'minimal', 'elegant']
        };
        
        const keywords = themeKeywords[theme] || [];
        const matches = product.tags.filter(tag => keywords.includes(tag)).length;
        return matches / keywords.length;
    }
    
    renderAISuggestions() {
        const container = $('.ai-suggestions');
        container.empty();
        
        if (this.aiSuggestions.length === 0) {
            container.append('<p class="text-muted">No suggestions available</p>');
            return;
        }
        
        this.aiSuggestions.forEach((suggestion, index) => {
            const suggestionProducts = suggestion.products.map(id => 
                this.availableProducts.find(p => p.id === id)
            ).filter(Boolean);
            
            const suggestionElement = $(`
                <div class="ai-suggestion" data-suggestion-index="${index}">
                    <div class="suggestion-header">
                        <h6 class="suggestion-title">${suggestion.title}</h6>
                        <div class="confidence-badge">
                            <i class="fas fa-brain me-1"></i>
                            ${Math.round(suggestion.confidence * 100)}%
                        </div>
                    </div>
                    <p class="suggestion-description">${suggestion.description}</p>
                    <div class="suggestion-products">
                        ${suggestionProducts.map(product => `
                            <div class="suggestion-product">
                                <img src="${product.image}" alt="${product.name}" class="suggestion-product-image">
                                <span class="suggestion-product-name">${product.name}</span>
                                <span class="suggestion-product-price">₹${product.price.toLocaleString()}</span>
                            </div>
                        `).join('')}
                    </div>
                    <p class="suggestion-reason"><i class="fas fa-lightbulb me-1"></i>${suggestion.reason}</p>
                    <button class="btn btn-outline-primary btn-sm apply-suggestion-btn" data-suggestion-index="${index}">
                        <i class="fas fa-magic me-1"></i>Apply Suggestion
                    </button>
                </div>
            `);
            
            container.append(suggestionElement);
        });
    }
    
    applySuggestion(suggestionIndex) {
        const suggestion = this.aiSuggestions[suggestionIndex];
        if (!suggestion) return;
        
        // Add all suggested products
        suggestion.products.forEach(productId => {
            if (!this.currentBundle.products.some(p => p.id === productId)) {
                this.addProductToBundle(productId);
            }
        });
        
        this.showAlert(`Applied suggestion: ${suggestion.title}`, 'success');
    }
    
    selectTheme(theme) {
        this.currentBundle.theme = theme;
        $('.theme-btn').removeClass('active');
        $(`.theme-btn[data-theme="${theme}"]`).addClass('active');
        this.calculateBundlePrice();
        this.updateBundleDisplay();
        this.generateAISuggestions();
    }
    
    selectOccasion(occasion) {
        this.currentBundle.occasion = occasion;
        $('.occasion-btn').removeClass('active');
        $(`.occasion-btn[data-occasion="${occasion}"]`).addClass('active');
        this.calculateBundlePrice();
        this.updateBundleDisplay();
        this.generateAISuggestions();
    }
    
    animateProductAddition(product) {
        // Create a temporary element for animation
        const tempElement = $(`
            <div class="product-animation">
                <img src="${product.image}" alt="${product.name}">
            </div>
        `);
        
        $('body').append(tempElement);
        
        // Animate from product card to bundle canvas
        const sourceCard = $(`.product-card[data-product-id="${product.id}"]`);
        const targetCanvas = $('.bundle-canvas');
        
        if (sourceCard.length && targetCanvas.length) {
            const sourcePos = sourceCard.offset();
            const targetPos = targetCanvas.offset();
            
            tempElement.css({
                position: 'fixed',
                left: sourcePos.left,
                top: sourcePos.top,
                width: '60px',
                height: '60px',
                zIndex: 9999,
                borderRadius: '8px',
                overflow: 'hidden'
            });
            
            tempElement.animate({
                left: targetPos.left + targetCanvas.width() / 2 - 30,
                top: targetPos.top + targetCanvas.height() / 2 - 30,
                opacity: 0.7
            }, 500, () => {
                tempElement.remove();
            });
        }
    }
    
    saveBundle() {
        if (this.currentBundle.products.length === 0) {
            this.showAlert('Please add products to your bundle first', 'warning');
            return;
        }
        
        if (!this.currentBundle.name.trim()) {
            this.currentBundle.name = `Bundle ${Date.now()}`;
        }
        
        // Send to backend
        $.ajax({
            url: '/api/bundle/save',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                name: this.currentBundle.name,
                products: this.currentBundle.products.map(p => p.id),
                theme: this.currentBundle.theme,
                occasion: this.currentBundle.occasion,
                total_price: this.currentBundle.totalPrice,
                discount_percentage: this.currentBundle.discountPercentage,
                final_price: this.currentBundle.finalPrice
            }),
            success: (response) => {
                this.showAlert('Bundle saved successfully!', 'success');
                this.currentBundle.id = response.bundle_id;
            },
            error: (xhr) => {
                console.error('Failed to save bundle:', xhr);
                this.showAlert('Failed to save bundle. Please try again.', 'error');
            }
        });
    }
    
    clearBundle() {
        this.currentBundle = {
            id: null,
            name: '',
            products: [],
            totalPrice: 0,
            discountPercentage: 0,
            finalPrice: 0,
            theme: '',
            occasion: ''
        };
        
        $('#bundleName').val('');
        $('.theme-btn, .occasion-btn').removeClass('active');
        this.updateBundleDisplay();
        this.renderProductGrid();
        this.generateAISuggestions();
        
        this.showAlert('Bundle cleared', 'info');
    }
    
    showAlert(message, type = 'info') {
        if (window.PersonaApp && window.PersonaApp.showAlert) {
            window.PersonaApp.showAlert(message, type);
        } else {
            console.log(`${type.toUpperCase()}: ${message}`);
        }
    }
}

// Initialize Bundle Builder when DOM is ready
$(document).ready(function() {
    if ($('.bundle-builder-container').length) {
        window.bundleBuilder = new BundleBuilder();
    }
});

// Export for use in other scripts
window.BundleBuilder = BundleBuilder;
