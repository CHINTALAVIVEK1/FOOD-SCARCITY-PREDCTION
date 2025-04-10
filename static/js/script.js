// Custom JavaScript for Food Scarcity Prediction System

$(document).ready(function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });
    
    // Add fade-in animation to cards
    $('.card').addClass('fade-in');
    
    // Add event listener for form submission
    $('#prediction-form').on('submit', function() {
        // Show loading spinner
        $('#submit-btn').html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...');
        $('#submit-btn').prop('disabled', true);
    });
    
    // Add event listeners for input fields
    $('#region, #crop, #season, #year').on('change', function() {
        validateForm();
    });
    
    // Function to validate form
    function validateForm() {
        var isValid = true;
        
        // Check if required fields are filled
        if (!$('#region').val()) isValid = false;
        if (!$('#crop').val()) isValid = false;
        if (!$('#season').val()) isValid = false;
        if (!$('#year').val()) isValid = false;
        
        // Enable/disable submit button
        $('#submit-btn').prop('disabled', !isValid);
    }
    
    // Initialize form validation
    validateForm();
    
    // Add smooth scrolling for anchor links
    $('a[href^="#"]').on('click', function(event) {
        var target = $(this.getAttribute('href'));
        if (target.length) {
            event.preventDefault();
            $('html, body').stop().animate({
                scrollTop: target.offset().top - 100
            }, 1000);
        }
    });
    
    // Add event listener for collapsible sections
    $('.collapse-toggle').on('click', function() {
        $(this).find('i').toggleClass('fa-chevron-down fa-chevron-up');
    });
    
    // Add event listener for theme toggle
    $('#theme-toggle').on('click', function() {
        $('body').toggleClass('dark-theme');
        $(this).find('i').toggleClass('fa-moon fa-sun');
        
        // Save preference to localStorage
        if ($('body').hasClass('dark-theme')) {
            localStorage.setItem('theme', 'dark');
        } else {
            localStorage.setItem('theme', 'light');
        }
    });
    
    // Check for saved theme preference
    var savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        $('body').addClass('dark-theme');
        $('#theme-toggle').find('i').removeClass('fa-moon').addClass('fa-sun');
    }
    
    // Add event listener for region and crop selection to update averages
    $('#region').on('change', function() {
        var region = $(this).val();
        if (region) {
            // Update population average
            $.getJSON('/api/region_stats/' + region, function(data) {
                if (!data.error) {
                    $('#population-help').text('Average population for ' + region + ': ' + data.avg_population.toLocaleString());
                }
            });
            
            // If crop is also selected, update production average
            var crop = $('#crop').val();
            if (crop) {
                $.getJSON('/api/region_crop_stats/' + region + '/' + crop, function(data) {
                    if (!data.error) {
                        $('#production-help').text('Average production for ' + crop + ' in ' + region + ': ' + data.avg_production.toLocaleString() + ' tonnes');
                    }
                });
            }
        }
    });
    
    $('#crop').on('change', function() {
        var crop = $(this).val();
        if (crop) {
            // Update production average
            var region = $('#region').val();
            if (region) {
                $.getJSON('/api/region_crop_stats/' + region + '/' + crop, function(data) {
                    if (!data.error) {
                        $('#production-help').text('Average production for ' + crop + ' in ' + region + ': ' + data.avg_production.toLocaleString() + ' tonnes');
                    } else {
                        $.getJSON('/api/crop_stats/' + crop, function(data) {
                            if (!data.error) {
                                $('#production-help').text('Average production for ' + crop + ': ' + data.avg_production.toLocaleString() + ' tonnes');
                            }
                        });
                    }
                });
            } else {
                $.getJSON('/api/crop_stats/' + crop, function(data) {
                    if (!data.error) {
                        $('#production-help').text('Average production for ' + crop + ': ' + data.avg_production.toLocaleString() + ' tonnes');
                    }
                });
            }
        }
    });
});
