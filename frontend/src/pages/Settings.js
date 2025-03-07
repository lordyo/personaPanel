import React, { useState, useEffect } from 'react';
import axios from 'axios';

const Settings = () => {
  const [settings, setSettings] = useState({
    model_settings: {
      model: 'gpt-4o-mini',
      temperature: 1.0,
      max_tokens: 1000,
      cache: false,
      cache_in_memory: false,
      provider: 'openai'
    }
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState('');

  // Available LLM models
  const availableModels = [
    { value: 'gpt-4o-mini', label: 'GPT-4o-mini (OpenAI)', provider: 'openai' },
    { value: 'gpt-4o', label: 'GPT-4o (OpenAI)', provider: 'openai' },
    { value: 'anthropic/claude-3-5-haiku-20241022', label: 'Claude 3.5 Haiku (Anthropic)', provider: 'anthropic' }
  ];

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get('/api/settings');
      console.log('Settings API response:', response.data);
      
      // Ensure we have the expected structure
      const receivedSettings = response.data;
      
      // If model_settings is missing, create it with defaults
      if (!receivedSettings.model_settings) {
        receivedSettings.model_settings = {
          model: 'gpt-4o-mini',
          temperature: 1.0,
          max_tokens: 1000,
          cache: false,
          cache_in_memory: false,
          provider: 'openai'
        };
      }
      
      // Ensure provider is set based on model if missing
      if (!receivedSettings.model_settings.provider) {
        const model = receivedSettings.model_settings.model;
        receivedSettings.model_settings.provider = model.includes('claude') ? 'anthropic' : 'openai';
      }

      // Ensure cache settings are defined
      if (receivedSettings.model_settings.cache === undefined) {
        receivedSettings.model_settings.cache = false;
      }
      if (receivedSettings.model_settings.cache_in_memory === undefined) {
        receivedSettings.model_settings.cache_in_memory = false;
      }
      
      setSettings(receivedSettings);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching settings:', err);
      setError('Failed to load settings. Please try again.');
      setLoading(false);
    }
  };

  const handleModelChange = (e) => {
    const selectedModel = e.target.value;
    const selectedProvider = availableModels.find(model => model.value === selectedModel)?.provider || 'openai';
    
    setSettings({
      ...settings,
      model_settings: {
        ...settings.model_settings,
        model: selectedModel,
        provider: selectedProvider
      }
    });
  };

  const handleTemperatureChange = (e) => {
    const value = parseFloat(e.target.value);
    setSettings({
      ...settings,
      model_settings: {
        ...settings.model_settings,
        temperature: value
      }
    });
  };

  const handleMaxTokensChange = (e) => {
    const value = parseInt(e.target.value);
    setSettings({
      ...settings,
      model_settings: {
        ...settings.model_settings,
        max_tokens: value
      }
    });
  };
  
  const handleCacheToggle = () => {
    setSettings({
      ...settings,
      model_settings: {
        ...settings.model_settings,
        cache: !settings.model_settings.cache
      }
    });
  };
  
  const handleCacheInMemoryToggle = () => {
    setSettings({
      ...settings,
      model_settings: {
        ...settings.model_settings,
        cache_in_memory: !settings.model_settings.cache_in_memory
      }
    });
  };

  const saveSettings = async () => {
    setSaving(true);
    setError(null);
    setSuccessMessage('');
    
    try {
      await axios.post('/api/settings', settings);
      setSuccessMessage('Settings saved successfully!');
      setSaving(false);
      
      // Clear success message after 3 seconds
      setTimeout(() => {
        setSuccessMessage('');
      }, 3000);
    } catch (err) {
      console.error('Error saving settings:', err);
      setError('Failed to save settings. Please try again.');
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="animate-pulse flex flex-col space-y-4">
          <div className="h-4 bg-gray-700 rounded w-1/4"></div>
          <div className="h-12 bg-gray-700 rounded w-full"></div>
          <div className="h-12 bg-gray-700 rounded w-full"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="bg-gray-800 shadow-lg rounded-lg overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-700">
          <h1 className="text-xl font-semibold text-white">Application Settings</h1>
        </div>
        
        <div className="p-6">
          {error && (
            <div className="mb-4 p-3 bg-red-900/50 border border-red-500 text-red-300 rounded">
              {error}
            </div>
          )}
          
          {successMessage && (
            <div className="mb-4 p-3 bg-green-900/50 border border-green-500 text-green-300 rounded">
              {successMessage}
            </div>
          )}
          
          <div className="mb-6">
            <h2 className="text-lg font-medium text-white mb-4">LLM Model Settings</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  LLM Model
                </label>
                <select
                  value={settings.model_settings.model}
                  onChange={handleModelChange}
                  className="w-full bg-gray-700 border border-gray-600 rounded py-2 px-3 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {availableModels.map(model => (
                    <option key={model.value} value={model.value}>
                      {model.label}
                    </option>
                  ))}
                </select>
                <p className="mt-1 text-sm text-gray-400">
                  Select the model to use for generating entities and simulations.
                </p>
                <div className="mt-2 text-xs text-blue-400 bg-blue-900/20 p-2 rounded border border-blue-800">
                  <p className="font-medium">Provider: {settings.model_settings.provider === 'openai' ? 'OpenAI' : 'Anthropic'}</p>
                  <p className="mt-1">Using API key from .env file: {settings.model_settings.provider === 'openai' ? 'OPENAI_API_KEY' : 'CLAUDE_API_KEY'}</p>
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Temperature (0.0 - 2.0)
                </label>
                <input
                  type="range"
                  min="0"
                  max="2"
                  step="0.1"
                  value={settings.model_settings.temperature}
                  onChange={handleTemperatureChange}
                  className="w-full bg-gray-700"
                />
                <div className="flex justify-between text-sm text-gray-400 mt-1">
                  <span>0.0 (More deterministic)</span>
                  <span className="font-medium text-white">{settings.model_settings.temperature.toFixed(1)}</span>
                  <span>2.0 (More creative)</span>
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Max Tokens
                </label>
                <input
                  type="number"
                  min="100"
                  max="4000"
                  step="50"
                  value={settings.model_settings.max_tokens}
                  onChange={handleMaxTokensChange}
                  className="w-full bg-gray-700 border border-gray-600 rounded py-2 px-3 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <p className="mt-1 text-sm text-gray-400">
                  Maximum number of tokens to generate in model responses.
                </p>
              </div>

              <div className="md:col-span-2">
                <h3 className="text-md font-medium text-white mb-3">Caching Options</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 bg-gray-700/50 p-4 rounded">
                  <div className="flex items-center">
                    <label className="flex items-center cursor-pointer">
                      <div className="relative">
                        <input 
                          type="checkbox" 
                          className="sr-only" 
                          checked={settings.model_settings.cache}
                          onChange={handleCacheToggle}
                        />
                        <div className={`block w-10 h-6 rounded-full ${settings.model_settings.cache ? 'bg-blue-500' : 'bg-gray-600'}`}></div>
                        <div className={`dot absolute left-1 top-1 bg-white w-4 h-4 rounded-full transition ${settings.model_settings.cache ? 'transform translate-x-4' : ''}`}></div>
                      </div>
                      <div className="ml-3 text-gray-300">
                        Enable LLM Response Caching
                      </div>
                    </label>
                    <div className="ml-2 text-xs text-gray-400">
                      (Saves API calls by reusing responses)
                    </div>
                  </div>
                  
                  <div className="flex items-center">
                    <label className="flex items-center cursor-pointer">
                      <div className="relative">
                        <input 
                          type="checkbox" 
                          className="sr-only" 
                          checked={settings.model_settings.cache_in_memory}
                          onChange={handleCacheInMemoryToggle}
                          disabled={!settings.model_settings.cache}
                        />
                        <div className={`block w-10 h-6 rounded-full ${settings.model_settings.cache_in_memory && settings.model_settings.cache ? 'bg-blue-500' : 'bg-gray-600'}`}></div>
                        <div className={`dot absolute left-1 top-1 bg-white w-4 h-4 rounded-full transition ${settings.model_settings.cache_in_memory && settings.model_settings.cache ? 'transform translate-x-4' : ''}`}></div>
                      </div>
                      <div className={`ml-3 ${settings.model_settings.cache ? 'text-gray-300' : 'text-gray-500'}`}>
                        Cache in Memory
                      </div>
                    </label>
                    <div className={`ml-2 text-xs ${settings.model_settings.cache ? 'text-gray-400' : 'text-gray-500'}`}>
                      (Faster but cleared on restart)
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div className="flex justify-end">
            <button
              onClick={saveSettings}
              disabled={saving}
              className={`px-4 py-2 rounded text-white font-medium ${
                saving 
                  ? 'bg-blue-800 cursor-not-allowed' 
                  : 'bg-blue-600 hover:bg-blue-700'
              }`}
            >
              {saving ? 'Saving...' : 'Save Settings'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings; 