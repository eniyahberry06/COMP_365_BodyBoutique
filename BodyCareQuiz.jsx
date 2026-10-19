import React, { useState } from 'react';

const CONCERN_OPTIONS = [
    'Acne',
    'Redness',
    'Dryness',
    'Eczema',
    'Fine Lines',
    'Hyperpigmentation',
    'Sensitive Skin',
    'Oil Control',
];

export default function BodyCareQuiz() {
    const [ingredientInput, setIngredientInput] = useState('');
    const [desiredIngredients, setDesiredIngredients] = useState(['Retinol', 'Niacinamide']);
    const [selectedConcerns, setSelectedConcerns] = useState([]);
    const [productType, setProductType] = useState('Serum');
    const [scentPreference, setScentPreference] = useState('unscented');
    const [texturePreference, setTexturePreference] = useState('gel');

    const [recommendations, setRecommendations] = useState([]);
    const [warnings, setWarnings] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const toggleConcern = (concern) => {
        setSelectedConcerns((prev) =>
            prev.includes(concern)
                ? prev.filter((c) => c !== concern)
                : [...prev, concern]
        );
    };

    const handleAddIngredient = (e) => {
        e.preventDefault();
        if (ingredientInput.trim() && !desiredIngredients.includes(ingredientInput.trim())) {
            setDesiredIngredients([...desiredIngredients, ingredientInput.trim()]);
            setIngredientInput('');
        }
    };

    const removeIngredient = (ing) => {
        setDesiredIngredients(desiredIngredients.filter((i) => i !== ing));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        const payload = {
            desired_ingredients: desiredIngredients,
            skin_concerns: selectedConcerns,
            product_type: productType !== 'any' ? productType : null,
            scent_preference: scentPreference,
            texture_preference: texturePreference,
        };

        try {
            const response = await fetch('http://127.0.0.1:8001/recommendations', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });

            if (!response.ok) {
                throw new Error(`Server returned status ${response.status}`);
            }

            const data = await response.json();
            setRecommendations(data.recommendations || []);
            setWarnings(data.warnings || []);
        } catch (err) {
            console.error('Error fetching recommendations:', err);
            setError('Backend server connection failed. Ensure FastAPI is running on http://127.0.0.1:8001.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{ minHeight: '100vh', backgroundColor: '#f8fafc', padding: '40px 16px', fontFamily: 'sans-serif', color: '#1f2937' }}>
            <div style={{ maxWidth: '800px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '32px' }}>

                {/* Header */}
                <header style={{ textAlign: 'center', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    <h1 style={{ fontSize: '36px', fontWeight: '800', color: '#db2777', margin: 0 }}>
                        The Body Boutique
                    </h1>
                    <p style={{ fontSize: '14px', color: '#4b5563', maxWidth: '450px', margin: '0 auto' }}>
                        Multi-attribute recommendations paired with deterministic clinical safety guardrails.
                    </p>
                </header>

                {/* Main Form */}
                <form onSubmit={handleSubmit} style={{ backgroundColor: '#ffffff', borderRadius: '24px', padding: '32px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', border: '1px solid #f3f4f6', display: 'flex', flexDirection: 'column', gap: '32px' }}>

                    {/* Step 1: Ingredients */}
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                            <span style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', width: '24px', height: '24px', borderRadius: '9999px', backgroundColor: '#fce7f3', color: '#db2777', fontSize: '12px', fontWeight: 'bold' }}>1</span>
                            <h2 style={{ fontSize: '16px', fontWeight: 'bold', color: '#111827', margin: 0 }}>Target Active Ingredients</h2>
                        </div>
                        <div style={{ display: 'flex', gap: '8px' }}>
                            <input
                                type="text"
                                value={ingredientInput}
                                onChange={(e) => setIngredientInput(e.target.value)}
                                onKeyDown={(e) => e.key === 'Enter' && handleAddIngredient(e)}
                                placeholder="e.g. Salicylic Acid, Vitamin C"
                                style={{ flex: 1, border: '1px solid #e5e7eb', borderRadius: '12px', padding: '10px 16px', fontSize: '14px', outline: 'none' }}
                            />
                            <button
                                onClick={handleAddIngredient}
                                type="button"
                                style={{ backgroundColor: '#db2777', color: '#ffffff', padding: '10px 20px', borderRadius: '12px', fontSize: '14px', fontWeight: '600', border: 'none', cursor: 'pointer' }}
                            >
                                Add
                            </button>
                        </div>

                        {/* Ingredient Pills */}
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', paddingTop: '4px' }}>
                            {desiredIngredients.map((ing) => (
                                <span key={ing} style={{ backgroundColor: '#fdf2f8', color: '#be185d', border: '1px solid #fce7f3', fontSize: '12px', padding: '6px 12px', borderRadius: '9999px', display: 'flex', alignItems: 'center', gap: '6px', fontWeight: '500' }}>
                                    {ing}
                                    <button
                                        type="button"
                                        onClick={() => removeIngredient(ing)}
                                        style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#9d174d', fontWeight: 'bold', fontSize: '14px' }}
                                    >
                                        ×
                                    </button>
                                </span>
                            ))}
                        </div>
                    </div>

                    <hr style={{ border: 'none', borderTop: '1px solid #f3f4f6', margin: 0 }} />

                    {/* Step 2: Skin Concerns (Interactive Buttons) */}
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                            <span style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', width: '24px', height: '24px', borderRadius: '9999px', backgroundColor: '#fce7f3', color: '#db2777', fontSize: '12px', fontWeight: 'bold' }}>2</span>
                            <h2 style={{ fontSize: '16px', fontWeight: 'bold', color: '#111827', margin: 0 }}>Skin Concerns</h2>
                        </div>
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                            {CONCERN_OPTIONS.map((concern) => {
                                const isSelected = selectedConcerns.includes(concern);
                                return (
                                    <button
                                        key={concern}
                                        type="button"
                                        onClick={() => toggleConcern(concern)}
                                        style={{
                                            fontSize: '12px',
                                            padding: '8px 14px',
                                            borderRadius: '12px',
                                            border: '1px solid',
                                            borderColor: isSelected ? '#db2777' : '#e5e7eb',
                                            backgroundColor: isSelected ? '#db2777' : '#ffffff',
                                            color: isSelected ? '#ffffff' : '#4b5563',
                                            fontWeight: '500',
                                            cursor: 'pointer',
                                            transition: 'all 0.2s ease',
                                        }}
                                    >
                                        {concern}
                                    </button>
                                );
                            })}
                        </div>
                    </div>

                    <hr style={{ border: 'none', borderTop: '1px solid #f3f4f6', margin: 0 }} />

                    {/* Step 3: Preferences */}
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                            <span style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', width: '24px', height: '24px', borderRadius: '9999px', backgroundColor: '#fce7f3', color: '#db2777', fontSize: '12px', fontWeight: 'bold' }}>3</span>
                            <h2 style={{ fontSize: '16px', fontWeight: 'bold', color: '#111827', margin: 0 }}>Format & Sensory Preferences</h2>
                        </div>
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
                            <div>
                                <label style={{ display: 'block', fontSize: '12px', fontWeight: '600', color: '#4b5563', marginBottom: '6px' }}>Product Type</label>
                                <select
                                    value={productType}
                                    onChange={(e) => setProductType(e.target.value)}
                                    style={{ width: '100%', border: '1px solid #e5e7eb', borderRadius: '12px', padding: '10px', fontSize: '12px', backgroundColor: '#ffffff', outline: 'none' }}
                                >
                                    <option value="any">Any Category</option>
                                    <option value="Serum">Serum</option>
                                    <option value="Moisturizer">Moisturizer</option>
                                    <option value="Cleanser">Cleanser</option>
                                    <option value="Toner">Toner</option>
                                </select>
                            </div>

                            <div>
                                <label style={{ display: 'block', fontSize: '12px', fontWeight: '600', color: '#4b5563', marginBottom: '6px' }}>Fragrance</label>
                                <select
                                    value={scentPreference}
                                    onChange={(e) => setScentPreference(e.target.value)}
                                    style={{ width: '100%', border: '1px solid #e5e7eb', borderRadius: '12px', padding: '10px', fontSize: '12px', backgroundColor: '#ffffff', outline: 'none' }}
                                >
                                    <option value="any">No Preference</option>
                                    <option value="unscented">Unscented / Fragrance-Free</option>
                                    <option value="scented">Scented / Fresh</option>
                                </select>
                            </div>

                            <div>
                                <label style={{ display: 'block', fontSize: '12px', fontWeight: '600', color: '#4b5563', marginBottom: '6px' }}>Texture</label>
                                <select
                                    value={texturePreference}
                                    onChange={(e) => setTexturePreference(e.target.value)}
                                    style={{ width: '100%', border: '1px solid #e5e7eb', borderRadius: '12px', padding: '10px', fontSize: '12px', backgroundColor: '#ffffff', outline: 'none' }}
                                >
                                    <option value="any">No Preference</option>
                                    <option value="gel">Gel (Lightweight)</option>
                                    <option value="cream">Cream (Rich)</option>
                                    <option value="lotion">Lotion (Balanced)</option>
                                    <option value="oil">Oil / Balm</option>
                                </select>
                            </div>
                        </div>
                    </div>

                    {/* Submit Button */}
                    <button
                        type="submit"
                        disabled={loading}
                        style={{ width: '100%', backgroundColor: '#db2777', color: '#ffffff', fontWeight: 'bold', padding: '14px', borderRadius: '12px', border: 'none', cursor: 'pointer', transition: 'opacity 0.2s' }}
                    >
                        {loading ? 'Running Multi-Attribute Search...' : 'Get Personalised Recommendations'}
                    </button>
                </form>

                {/* Error Banner */}
                {error && (
                    <div style={{ backgroundColor: '#fef2f2', color: '#b91c1c', padding: '16px', borderRadius: '16px', fontSize: '14px', border: '1px solid #fee2e2', display: 'flex', alignItems: 'center', gap: '12px' }}>
                        <span>⚠️</span>
                        <span>{error}</span>
                    </div>
                )}

                {/* Warnings */}
                {warnings.length > 0 && (
                    <div style={{ backgroundColor: '#fffbeb', border: '1px solid #fde68a', color: '#92400e', padding: '20px', borderRadius: '16px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontWeight: 'bold', fontSize: '14px' }}>
                            <span>🛡️</span>
                            <h3>Clinical Safety Warnings Triggered:</h3>
                        </div>
                        <ul style={{ margin: 0, paddingLeft: '24px', fontSize: '12px', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                            {warnings.map((warn, index) => (
                                <li key={index}>{warn}</li>
                            ))}
                        </ul>
                    </div>
                )}

                {/* Results Grid */}
                {recommendations.length > 0 && (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                        <h3 style={{ fontSize: '20px', fontWeight: 'bold', color: '#111827', margin: 0, paddingLeft: '4px' }}>Recommended Products</h3>
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '24px' }}>
                            {recommendations.map((item, index) => (
                                <div key={index} style={{ backgroundColor: '#ffffff', borderRadius: '16px', padding: '24px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', border: '1px solid #f3f4f6', display: 'flex', flexDirection: 'column', justifyContent: 'space-between', gap: '16px' }}>
                                    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                            <span style={{ fontSize: '10px', fontWeight: 'bold', color: '#db2777', backgroundColor: '#fdf2f8', border: '1px solid #fce7f3', padding: '4px 10px', borderRadius: '9999px', textTransform: 'uppercase' }}>
                                                {item.product_type || 'Skincare'}
                                            </span>
                                            {item.price && (
                                                <span style={{ fontSize: '12px', fontWeight: 'bold', color: '#6b7280' }}>{item.price}</span>
                                            )}
                                        </div>

                                        <h4 style={{ fontSize: '16px', fontWeight: 'bold', color: '#111827', margin: 0, lineHeight: '1.4' }}>
                                            {item.product_name}
                                        </h4>

                                        <div style={{ backgroundColor: '#f8fafc', border: '1px solid #f1f5f9', borderRadius: '12px', padding: '14px', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                                            <p style={{ fontSize: '11px', fontWeight: 'bold', color: '#334155', textTransform: 'uppercase', margin: 0 }}>
                                                Why this product?
                                            </p>
                                            <p style={{ fontSize: '12px', color: '#4b5563', margin: 0, lineHeight: '1.5' }}>
                                                {item.match_reason || 'Matches target ingredients and sensory attributes.'}
                                            </p>
                                        </div>

                                        <p style={{ fontSize: '12px', color: '#6b7280', margin: 0, lineHeight: '1.5' }}>
                                            <span style={{ fontWeight: '600', color: '#374151' }}>Ingredients:</span> {item.clean_ingreds}
                                        </p>
                                    </div>

                                    {item.product_url && (
                                        <a
                                            href={item.product_url}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            style={{ width: '100%', textAlign: 'center', fontSize: '12px', fontWeight: 'bold', color: '#db2777', border: '1px solid #fce7f3', backgroundColor: '#fdf2f8', padding: '10px', borderRadius: '12px', display: 'block', textDecoration: 'none', boxSizing: 'border-box' }}
                                        >
                                            View Product Details
                                        </a>
                                    )}
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}