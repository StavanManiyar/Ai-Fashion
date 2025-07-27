-- Add specific Monk skin tone color recommendations
-- This adds the specific Monk01-Monk10 entries that our API expects

-- Insert color recommendations for Monk 1 (Very Light)
INSERT INTO colors (hex_code, color_name, suitable_skin_tone, seasonal_palette, category) VALUES
('#003057', 'Navy Blue', 'Monk01', 'Light Spring', 'recommended'),
('#F395C7', 'Soft Pink', 'Monk01', 'Light Spring', 'recommended'),
('#A277A6', 'Lavender', 'Monk01', 'Light Spring', 'recommended'),
('#009775', 'Emerald', 'Monk01', 'Light Spring', 'recommended'),
('#890C58', 'Burgundy', 'Monk01', 'Light Spring', 'recommended'),
('#0057B8', 'Cobalt Blue', 'Monk01', 'Light Spring', 'recommended'),
('#F88379', 'Soft Coral', 'Monk01', 'Light Spring', 'recommended'),
('#9BCBEB', 'Powder Blue', 'Monk01', 'Light Spring', 'recommended'),
('#FFA500', 'Orange', 'Monk01', 'Light Spring', 'avoid'),
('#800000', 'Maroon', 'Monk01', 'Light Spring', 'avoid');

-- Insert color recommendations for Monk 2 (Light)
INSERT INTO colors (hex_code, color_name, suitable_skin_tone, seasonal_palette, category) VALUES
('#9BCBEB', 'Powder Blue', 'Monk02', 'Light Spring', 'recommended'),
('#86647A', 'Soft Plum', 'Monk02', 'Light Spring', 'recommended'),
('#D592AA', 'Dusty Rose', 'Monk02', 'Light Spring', 'recommended'),
('#57728B', 'Slate Blue', 'Monk02', 'Light Spring', 'recommended'),
('#00B0B9', 'Soft Teal', 'Monk02', 'Light Spring', 'recommended'),
('#C4A4A7', 'Mauve', 'Monk02', 'Light Spring', 'recommended'),
('#F08080', 'Light Coral', 'Monk02', 'Light Spring', 'recommended'),
('#CCCCFF', 'Periwinkle', 'Monk02', 'Light Spring', 'recommended'),
('#8B4513', 'Saddle Brown', 'Monk02', 'Light Spring', 'avoid'),
('#2F4F4F', 'Dark Slate Gray', 'Monk02', 'Light Spring', 'avoid');

-- Insert color recommendations for Monk 3 (Light Medium)
INSERT INTO colors (hex_code, color_name, suitable_skin_tone, seasonal_palette, category) VALUES
('#FCC89B', 'Peach', 'Monk03', 'Clear Spring', 'recommended'),
('#A5DFD3', 'Mint', 'Monk03', 'Clear Spring', 'recommended'),
('#FF8D6D', 'Coral', 'Monk03', 'Clear Spring', 'recommended'),
('#F5E1A4', 'Light Yellow', 'Monk03', 'Clear Spring', 'recommended'),
('#A4DBE8', 'Aqua', 'Monk03', 'Clear Spring', 'recommended'),
('#FAAA8D', 'Soft Pink', 'Monk03', 'Clear Spring', 'recommended'),
('#FBCEB1', 'Apricot', 'Monk03', 'Clear Spring', 'recommended'),
('#87CEEB', 'Sky Blue', 'Monk03', 'Clear Spring', 'recommended'),
('#000080', 'Navy', 'Monk03', 'Clear Spring', 'avoid'),
('#4B0082', 'Indigo', 'Monk03', 'Clear Spring', 'avoid');

-- Insert color recommendations for Monk 4 (Medium Light)
INSERT INTO colors (hex_code, color_name, suitable_skin_tone, seasonal_palette, category) VALUES
('#FDAA63', 'Warm Beige', 'Monk04', 'Warm Spring', 'recommended'),
('#FFB81C', 'Golden Yellow', 'Monk04', 'Warm Spring', 'recommended'),
('#FF8F1C', 'Apricot', 'Monk04', 'Warm Spring', 'recommended'),
('#FFA38B', 'Coral', 'Monk04', 'Warm Spring', 'recommended'),
('#74AA50', 'Warm Green', 'Monk04', 'Warm Spring', 'recommended'),
('#2DCCD3', 'Turquoise', 'Monk04', 'Warm Spring', 'recommended'),
('#E6C200', 'Honey', 'Monk04', 'Warm Spring', 'recommended'),
('#FF8C00', 'Warm Orange', 'Monk04', 'Warm Spring', 'recommended'),
('#800080', 'Purple', 'Monk04', 'Warm Spring', 'avoid'),
('#708090', 'Slate Gray', 'Monk04', 'Warm Spring', 'avoid');

-- Insert color recommendations for Monk 5 (Medium)
INSERT INTO colors (hex_code, color_name, suitable_skin_tone, seasonal_palette, category) VALUES
('#008EAA', 'Turquoise', 'Monk05', 'Soft Autumn', 'recommended'),
('#FFCD00', 'Clear Yellow', 'Monk05', 'Soft Autumn', 'recommended'),
('#FF8D6D', 'Bright Coral', 'Monk05', 'Soft Autumn', 'recommended'),
('#963CBD', 'Violet', 'Monk05', 'Soft Autumn', 'recommended'),
('#00A499', 'Bright Green', 'Monk05', 'Soft Autumn', 'recommended'),
('#E40046', 'Watermelon', 'Monk05', 'Soft Autumn', 'recommended'),
('#FFBF00', 'Amber', 'Monk05', 'Soft Autumn', 'recommended'),
('#4169E1', 'Royal Blue', 'Monk05', 'Soft Autumn', 'recommended'),
('#F0E68C', 'Khaki', 'Monk05', 'Soft Autumn', 'avoid'),
('#B22222', 'Fire Brick', 'Monk05', 'Soft Autumn', 'avoid');

-- Insert color recommendations for Monk 6 (Medium Dark)
INSERT INTO colors (hex_code, color_name, suitable_skin_tone, seasonal_palette, category) VALUES
('#B89D18', 'Mustard', 'Monk06', 'Warm Autumn', 'recommended'),
('#9D4815', 'Rust', 'Monk06', 'Warm Autumn', 'recommended'),
('#A09958', 'Olive', 'Monk06', 'Warm Autumn', 'recommended'),
('#C4622D', 'Burnt Orange', 'Monk06', 'Warm Autumn', 'recommended'),
('#00778B', 'Teal', 'Monk06', 'Warm Autumn', 'recommended'),
('#205C40', 'Forest Green', 'Monk06', 'Warm Autumn', 'recommended'),
('#B87333', 'Copper', 'Monk06', 'Warm Autumn', 'recommended'),
('#B8860B', 'Deep Gold', 'Monk06', 'Warm Autumn', 'recommended'),
('#FF69B4', 'Hot Pink', 'Monk06', 'Warm Autumn', 'avoid'),
('#00FFFF', 'Cyan', 'Monk06', 'Warm Autumn', 'avoid');

-- Insert color recommendations for Monk 7 (Dark)
INSERT INTO colors (hex_code, color_name, suitable_skin_tone, seasonal_palette, category) VALUES
('#890C58', 'Burgundy', 'Monk07', 'Deep Autumn', 'recommended'),
('#5C462B', 'Chocolate', 'Monk07', 'Deep Autumn', 'recommended'),
('#00594C', 'Deep Teal', 'Monk07', 'Deep Autumn', 'recommended'),
('#9D4815', 'Rust', 'Monk07', 'Deep Autumn', 'recommended'),
('#5E7E29', 'Olive', 'Monk07', 'Deep Autumn', 'recommended'),
('#A6631B', 'Terracotta', 'Monk07', 'Deep Autumn', 'recommended'),
('#228B22', 'Forest Green', 'Monk07', 'Deep Autumn', 'recommended'),
('#CD7F32', 'Bronze', 'Monk07', 'Deep Autumn', 'recommended'),
('#FFB6C1', 'Light Pink', 'Monk07', 'Deep Autumn', 'avoid'),
('#E0E0E0', 'Light Gray', 'Monk07', 'Deep Autumn', 'avoid');

-- Insert color recommendations for Monk 8 (Very Dark)
INSERT INTO colors (hex_code, color_name, suitable_skin_tone, seasonal_palette, category) VALUES
('#E3006D', 'Hot Pink', 'Monk08', 'Deep Winter', 'recommended'),
('#0057B8', 'Cobalt Blue', 'Monk08', 'Deep Winter', 'recommended'),
('#CE0037', 'True Red', 'Monk08', 'Deep Winter', 'recommended'),
('#963CBD', 'Violet', 'Monk08', 'Deep Winter', 'recommended'),
('#009775', 'Emerald', 'Monk08', 'Deep Winter', 'recommended'),
('#FFB81C', 'Gold', 'Monk08', 'Deep Winter', 'recommended'),
('#800080', 'Royal Purple', 'Monk08', 'Deep Winter', 'recommended'),
('#FFCD00', 'Bright Yellow', 'Monk08', 'Deep Winter', 'recommended'),
('#D2B48C', 'Tan', 'Monk08', 'Deep Winter', 'avoid'),
('#F5DEB3', 'Wheat', 'Monk08', 'Deep Winter', 'avoid');

-- Insert color recommendations for Monk 9 (Deep)
INSERT INTO colors (hex_code, color_name, suitable_skin_tone, seasonal_palette, category) VALUES
('#890C58', 'Deep Claret', 'Monk09', 'Cool Winter', 'recommended'),
('#00594C', 'Forest Green', 'Monk09', 'Cool Winter', 'recommended'),
('#CE0037', 'True Red', 'Monk09', 'Cool Winter', 'recommended'),
('#002D72', 'Navy', 'Monk09', 'Cool Winter', 'recommended'),
('#84329B', 'Amethyst', 'Monk09', 'Cool Winter', 'recommended'),
('#FEFEFE', 'White', 'Monk09', 'Cool Winter', 'recommended'),
('#C0C0C0', 'Silver', 'Monk09', 'Cool Winter', 'recommended'),
('#301934', 'Deep Purple', 'Monk09', 'Cool Winter', 'recommended'),
('#D2691E', 'Chocolate', 'Monk09', 'Cool Winter', 'avoid'),
('#F4A460', 'Sandy Brown', 'Monk09', 'Cool Winter', 'avoid');

-- Insert color recommendations for Monk 10 (Deepest)
INSERT INTO colors (hex_code, color_name, suitable_skin_tone, seasonal_palette, category) VALUES
('#E3006D', 'Hot Pink', 'Monk10', 'Clear Winter', 'recommended'),
('#0057B8', 'Cobalt Blue', 'Monk10', 'Clear Winter', 'recommended'),
('#CE0037', 'True Red', 'Monk10', 'Clear Winter', 'recommended'),
('#FFCD00', 'Bright Yellow', 'Monk10', 'Clear Winter', 'recommended'),
('#009775', 'Emerald', 'Monk10', 'Clear Winter', 'recommended'),
('#FEFEFE', 'White', 'Monk10', 'Clear Winter', 'recommended'),
('#0000FF', 'Electric Blue', 'Monk10', 'Clear Winter', 'recommended'),
('#66FF00', 'Bright Green', 'Monk10', 'Clear Winter', 'recommended'),
('#800000', 'Maroon', 'Monk10', 'Clear Winter', 'avoid'),
('#556B2F', 'Dark Olive Green', 'Monk10', 'Clear Winter', 'avoid');

-- Verification query
SELECT 
    suitable_skin_tone, 
    category, 
    COUNT(*) as color_count 
FROM colors 
WHERE suitable_skin_tone LIKE 'Monk%'
GROUP BY suitable_skin_tone, category 
ORDER BY suitable_skin_tone, category;
