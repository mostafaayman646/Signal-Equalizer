/**
 * Audio Synchronization Script
 * Provides precise audio-cursor synchronization
 *
 * Usage: Add to assets folder, Dash will auto-include it
 */

(function() {
    'use strict';

    let audioPlayer = null;
    let syncInterval = null;
    let isPlaying = false;

    // Wait for DOM to be ready
    document.addEventListener('DOMContentLoaded', function() {
        initializeAudioSync();
    });

    function initializeAudioSync() {
        // Get audio player element
        audioPlayer = document.getElementById('cine-audio-player');

        if (!audioPlayer) {
            console.warn('Audio player not found, retrying...');
            setTimeout(initializeAudioSync, 1000);
            return;
        }

        // Add event listeners
        audioPlayer.addEventListener('play', onAudioPlay);
        audioPlayer.addEventListener('pause', onAudioPause);
        audioPlayer.addEventListener('timeupdate', onTimeUpdate);
        audioPlayer.addEventListener('ended', onAudioEnded);

        console.log('Audio sync initialized');
    }

    function onAudioPlay() {
        isPlaying = true;
        startSync();
    }

    function onAudioPause() {
        isPlaying = false;
        stopSync();
    }

    function onAudioEnded() {
        isPlaying = false;
        stopSync();

        // Trigger stop in Dash
        const stopButton = document.getElementById('cine-stop');
        if (stopButton) {
            stopButton.click();
        }
    }

    function onTimeUpdate() {
        if (!audioPlayer) return;

        const currentTime = audioPlayer.currentTime;
        const duration = audioPlayer.duration;

        // Update cursor position in Dash store (if accessible)
        // This would require clientside callbacks for full integration
        updateCursorPosition(currentTime);
    }

    function startSync() {
        if (syncInterval) return;

        // Sync cursor with audio every 50ms
        syncInterval = setInterval(function() {
            if (!isPlaying || !audioPlayer) {
                stopSync();
                return;
            }

            const currentTime = audioPlayer.currentTime;
            updateCursorPosition(currentTime);
        }, 50);
    }

    function stopSync() {
        if (syncInterval) {
            clearInterval(syncInterval);
            syncInterval = null;
        }
    }

    function updateCursorPosition(time) {
        // This would update the Dash store with current playback position
        // For full implementation, use Dash clientside callbacks

        // Example: Dispatch custom event that Dash can listen to
        const event = new CustomEvent('audio-time-update', {
            detail: { currentTime: time }
        });
        document.dispatchEvent(event);
    }

    // Public API for Dash to control audio
    window.CineAudioController = {
        play: function() {
            if (audioPlayer) {
                audioPlayer.play();
            }
        },

        pause: function() {
            if (audioPlayer) {
                audioPlayer.pause();
            }
        },

        stop: function() {
            if (audioPlayer) {
                audioPlayer.pause();
                audioPlayer.currentTime = 0;
            }
        },

        seek: function(time) {
            if (audioPlayer) {
                audioPlayer.currentTime = time;
            }
        },

        setPlaybackRate: function(rate) {
            if (audioPlayer) {
                audioPlayer.playbackRate = rate;
            }
        },

        getCurrentTime: function() {
            return audioPlayer ? audioPlayer.currentTime : 0;
        },

        getDuration: function() {
            return audioPlayer ? audioPlayer.duration : 0;
        }
    };

})();