#!/bin/bash

# Symmetra Documentation Build Script
set -e

echo "🚀 Building Symmetra Documentation"

# Check if we're in the right directory
if [ ! -f "mkdocs.yml" ]; then
    echo "❌ Error: mkdocs.yml not found. Please run from the repository root."
    exit 1
fi

# Install documentation dependencies
echo "📦 Installing documentation dependencies..."
if command -v uv >/dev/null 2>&1; then
    uv pip install -r requirements-docs.txt
else
    pip install -r requirements-docs.txt
fi

# Build the documentation
echo "🔨 Building documentation site..."
mkdocs build --clean --strict

# Check for broken links (if available)
if command -v linkchecker >/dev/null 2>&1; then
    echo "🔍 Checking for broken links..."
    linkchecker site/index.html
else
    echo "ℹ️  Skipping link check (linkchecker not installed)"
fi

# Optimize images (if available)
if command -v imageoptim >/dev/null 2>&1; then
    echo "🖼️  Optimizing images..."
    find site/ -name "*.png" -o -name "*.jpg" -o -name "*.jpeg" | xargs imageoptim
else
    echo "ℹ️  Skipping image optimization (imageoptim not installed)"
fi

# Generate sitemap
echo "🗺️  Generating sitemap..."
cat > site/sitemap.xml << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://docs.symmetra.dev/</loc>
        <lastmod>$(date +%Y-%m-%d)</lastmod>
        <changefreq>weekly</changefreq>
        <priority>1.0</priority>
    </url>
    <url>
        <loc>https://docs.symmetra.dev/getting-started/quickstart/</loc>
        <lastmod>$(date +%Y-%m-%d)</lastmod>
        <changefreq>weekly</changefreq>
        <priority>0.9</priority>
    </url>
</urlset>
EOF

# Create robots.txt
echo "🤖 Creating robots.txt..."
cat > site/robots.txt << 'EOF'
User-agent: *
Allow: /

Sitemap: https://docs.symmetra.dev/sitemap.xml
EOF

# Build statistics
echo ""
echo "📊 Build Statistics:"
echo "   Total files: $(find site/ -type f | wc -l)"
echo "   HTML files: $(find site/ -name "*.html" | wc -l)"
echo "   CSS files: $(find site/ -name "*.css" | wc -l)"
echo "   JS files: $(find site/ -name "*.js" | wc -l)"
echo "   Images: $(find site/ -name "*.png" -o -name "*.jpg" -o -name "*.jpeg" -o -name "*.gif" -o -name "*.svg" | wc -l)"

# Total size
TOTAL_SIZE=$(du -sh site/ | cut -f1)
echo "   Total size: $TOTAL_SIZE"

echo ""
echo "✅ Documentation build complete!"
echo "   Site generated in: ./site/"
echo "   Preview locally: mkdocs serve"
echo "   Deploy to GitHub Pages: mkdocs gh-deploy"

# Optional: Start development server
if [ "$1" = "--serve" ]; then
    echo ""
    echo "🌐 Starting development server..."
    mkdocs serve
fi