/**
 * Ploud > global.js
 */

;(function() {

  /**
   * jQuery toggleFade
   *
   * @author      nerdfiles
   * @usage
   *              $(selector).toggleFade(speed);
   *
   */

  $.fn.toggleFade = function(speed, onbefore, onafter) {

      return this.each(function(e) {

          var $self = $(this),
              d = $self.css("display");

          if ( d === "none" || d === '' ) {
              if ( typeof(onbefore) === 'function' ) {
                  onbefore();
              }
              //$self.addClass('toggleFade-show');
              $self.fadeIn(speed, onafter);

          } else {
              if ( typeof(onbefore) === 'function' ) {
                  onbefore();
              }
              //$self.removeClass('toggleFade-show');
              $self.fadeOut(speed, onafter);

          }

      });

  } // End $.fn.toggleFade

  var Ploud = {

      validationSetup: function() {

        /**
         * jQuery Validation (Custom)
         *
         * @author      nerdfiles
         * @see         http://bassistance.de/jquery-plugins/jquery-plugin-validation/
         */

        /* jQuery Metadata Plugin (Dependency) */

        $.metadata.setType("attr", "validate");

        /* Custom Validator Methods */

        /* Custom Validator Defaults */

        jQuery.validator.setDefaults({
            onkeyup: false,
            onfocusout: false,
            onsubmit: true,
            errorPlacement: function(error, element) {
                element.parent().parent().append(error);
            },
            invalidHandler: function(form, validator) {
                var errors = validator.numberOfInvalids();
                var $form = $(form.currentTarget);
                if (errors) {
                    var message = errors == 1
                            ? '<p>Please review the error below. It has been marked.</p>'
                            : '<p>Please review the ' + errors + ' errors below. Errors have been marked.</p>';

                    $form.find("div.mod-status-message .status-content").html(message);
                    $form.find("div.mod-status-message h3").text("Please correct form errors");
                    $form.find("div.mod-status-message").addClass('error').animate({
                        opacity: 'hide'
                    }, 500).fadeIn('fast').removeClass('hide');

                } else {
                    $form.find("div.mod-status-message").hide();
                }
            }

        });

        /**
         * jQuery Validation Ploud Implementation
         *
         * @author      nerdfiles
         */

        /**
         * Ploud Login
         */

        $('#ploud-login #login-email').attr('validate', '{required:true,email:true}');
        $('#ploud-login #login-password').attr('validate', '{required:true}');
        $('#ploud-login').validate({
            submitHandler: function(form) {
                var action = form.action;

                $.ajax({
                    url:        action + '/validate',
                    type:       'post',
                    data:       $(form).serialize(),
                    success:    function(data, textStatus, xhr) {
                        if ( $.isEmptyObject(data) ) {
                            form.submit();
                        } else {
                            // errors in obj
                            for ( var i in data ) {
                                var id = i,
                                    msg = data[i];

                                $('#'+id).parent().parent().append('<label for="'+id+'" class="error" generated="true">'+msg+'</label>');
                            }
                        }
                    }
                });

            },
            invalidHandler: null
        });

        /**
         * Ploud Signup
         */
        $('#ploud-signup #signup-email').attr('validate', '{required:true,email:true}');
        $('#ploud-signup #signup-site-name').attr('validate', '{required:true}');
        $('#ploud-signup #signup-accept-toc').attr('validate', '{required:true}');
        $('#ploud-signup').validate({
          invalidHandler: null,
          submitHandler: function(form) {
              var action = form.action;

              $.ajax({
                  url:        action + '/validate',
                  type:       'post',
                  data:       $(form).serialize(),
                  error:      function() {
                  },
                  success:    function(data, textStatus, xhr) {
                        if ( $.isEmptyObject(data) ) {
                            form.submit();
                        } else {
                            // errors in obj
                            for ( var i in data ) {
                                var id = i,
                                    msg = data[i];

                                $('#'+id).parent().parent().append('<label for="'+id+'" class="error" generated="true">'+msg+'</label>');
                            }
                        }

                  }
              }); // ajax
          }
        });

        /**
         * Ploud Create Site (Dashboard)
         */

        $('#ploud-createsite #createsite-site-name').attr('validate', '{required:true}');
        $('#ploud-createsite #createsite-site-type').attr('validate', '{required:true}');
        $('#ploud-createsite').validate({
            invalidHandler: null
        });

        /**
         * Ploud Reset Password
         */

        $('#ploud-resetpw #login-email').attr('validate', '{required:true,email:true}');
        $('#ploud-resetpw').validate({
          invalidHandler: null,
          submitHandler: function(form) {
            var action = form.action;

            $.ajax({
              url:        action + '/validate',
              type:       'post',
              data:       $(form).serialize(),
              success:    function(data, textStatus, xhr) {
                if ( $.isEmptyObject(data) ) {
                    form.submit();
                } else {
                              for ( var i in data ) {
                    var id = i,
                      msg = data[i];

                    $('#'+id).parent().parent().append('<label for="'+id+'" class="error" generated="true">'+msg+'</label>');
                              }
                              if ($.isEmptyObject(data)) {
                                  window.location = '/';
                              }
                            }
              }
            });
          }
        });

        /**
         * Ploud Change Password
         */

        $('#ploud-changepw #change-password').attr('validate', '{required:true}');
        $('#ploud-changepw #confirm-password').attr('validate', '{required:true,equalTo:"#change-password"}');
        $('#ploud-changepw').validate({
            invalidHandler: null
        });

        /**
         * Ploud Quick Profile
         *
         * @deprecated  true
         */

        $('#ploud-quickprofile #login-email').attr('validate', '{email:true}');
        $('#ploud-quickprofile #change-password').attr('validate', '{required:true}');
        $('#ploud-quickprofile #confirm-password').attr('validate', '{required:true,equalTo:"#change-password"}');
        $('#ploud-quickprofile').validate();

        /**
         * Ploud Profile
         *
         * @deprecated  true
         */

        $('#ploud-profile #login-email').attr('validate', '{email:true}');
        $('#ploud-profile #change-password').attr('validate', '{required:true}');
        $('#ploud-profile #confirm-password').attr('validate', '{required:true,equalTo:"#change-password"}');
        $('#ploud-profile').validate()

        /**
         * Ploud Change Site Name (Dashbord)
         */

        $('#ploud-changenameofsite #changenameofsite-sitename').attr('validate', '{required:true}');
        $('#ploud-changenameofsite').validate();

        /**
         * Ploud Transfer Site (Dashbord)
         */

        $('#ploud-transfersite #transfersite-newowner').attr('validate', '{required:true,email:true}');
        $('#ploud-transfersite').validate();

    $('.action_change').click(function() {
        var form = $('#ploud-changenameofsite').get(0);
        var action = $(this).attr('href');
        form.setAttribute('action', action);
    });
    $('.action_transfer').click(
        function() {
            $('#ploud-transfer-site').val($(this).attr('site'));
        }
    );
    $('#ploud-transfer').validate({
         invalidHandler: null,
         submitHandler: function(form) {
             var action = form.action;

                    $.ajax({
                 url:        '/actions.html/validateTransfer',
                 type:       'post',
                 data:       $(form).serialize(),
                 success:    function(data, textStatus, xhr) {
                     if ( $.isEmptyObject(data) ) {
                         form.submit();
                     } else {
                         for ( var i in data ) {
                             var id = i,
                                 msg = data[i];

                             $('#transfer-'+id).parent().parent().append('<label for="transfer-'+id+'" class="error" generated="true">'+msg+'</label>');
                         }
                            }
                 }
             });
         }
    });

    /**
     * remove site
     */
    $('.action_remove').click(
         function() {
             $('#ploud-remove-site').val($(this).attr('site'));
            $('#remove-1 .sitename').html($(this).attr('href'));
         }
    );

      },

      setUpColorbox: function() {

          $('.colorbox').each(function() {

              var $self = $(this),
                  href = $(this).attr('class').match(/modal-cta-find:([A-Za-z0-9\-]+)/),
                  href = '#'+href[1];

              $self.colorbox({
                  onOpen: function() {

                      $('#colorbox').hide();

                  },
                  onComplete: function() {
                      var $closeClone = $('#cboxClose'),
                          $anyModModalContent = $('#colorbox .mod .mod-inner');

                      $closeClone.appendTo($anyModModalContent);

                      $anyModModalContent.addClass('focus');

                      $anyModModalContent.bind('mouseover', function() {
                          $(this).addClass('hover');
                      });

                      $anyModModalContent.bind('mouseout', function() {
                          $(this).removeClass('focus');
                          $(this).removeClass('hover');
                      });

                  },
                  onLoad: function() {

                      $('#colorbox').fadeIn('fast').focus();

                  },

                  /**
                   * defer height and width responsibility to css (by default)

                  height: '50%',
                  width: '50%',

                   */

                  transition: 'none',
                  height: "100%",
                  inline: true,
                  href: href
              });

          });

      },

      kbdOnButtons: function() {

          $('.button').each(function() {
              var $self = $(this);

              $self.bind('keydown keyup', function(e) {

                  if ( e.type === 'keydown' ) {
                      $self.css({
                          position: 'relative',
                          top: '1px'
                      });
                  } else if ( e.type === 'keyup' ) {

                      $self.css({
                          top: '0px'
                      });

                  }

              });
          });

      },

      toggleDashboardActionsMenu: function() {

          $('.site-actions-menu').prev().bind('click', function(e) {
              var $self = $(this),
                  $selfActionMenu = $self.next(),
                  $allActionMenus = $('.site-actions-menu'),
                  $allActionMenuTriggers = $allActionMenus.prev(),
                  anyActive = $('.site-actions-menu.active').length;

              if ( anyActive > 0 && !$self.hasClass('active') ) {
                  $('.site-actions-menu.active')
                      .removeClass('active')
                      .fadeOut('fast')
                      .prev()
                      .removeClass('active');
              }

              $('body').unbind('click.clearAll');

              $self
                  .addClass('active');

              $selfActionMenu
                  .addClass('active')
                  .fadeIn('fast', function() {

                      $('.site-actions-menu.active').bind('click.clearAll', function(e) {
                          var tgt = e.target.nodeName;

                          if ( tgt == 'DIV' || tgt == 'SPAN' ) {
                              e.stopPropagation();
                          }
                      });

                      $('body').bind('click.clearAll', function(e) {
                          $('.site-actions-menu.active')
                              .removeClass('active')
                              .fadeOut('fast')
                              .prev()
                              .removeClass('active');

                          $('body').unbind('click.clearAll');
                      });

                  });

              e.preventDefault();
          });

      },

      closeActionMenus: function() {
          $('.site-actions-menu .close').bind('click', function() {
              var $self = $(this),
                  d = $self.css('display');

              function onafter() {
                  $self.parent().prev().removeClass('active');
              }

              $self.parent().toggleFade('fast', null, onafter);
          });
      },

      customSelect: function() {

          $('ul.custom-select').live('click', function(e) {

              var $self = $(this);

              $self.find('li').each(function() {
                  $(this).removeClass('hide');
              });

              $self.addClass('expanded');

              $self.find('li').bind('click', function(e) {
                  var $li = $(this),
                      val = $li.attr('class').match(/value:([A-Za-z0-9]+)/),
                      val = (val) ? val[1] : '',
                      $selected = $li.parent().parent().prev().find('option[value="'+val+'"]');

                  $self.parent().find('.selected').remove();

                  $selected.prop('selected', 'selected');
                  $self.prepend('<li class="selected">'+$li.text()+'</li>');

                  $self.find('li:gt(0)').each(function() {
                      $(this).addClass('hide');

                      e.stopPropagation();
                  });

                  $self.removeClass('expanded');
                  $self.find('li').unbind('click');

              });

              function cb() {
                  $('ul.custom-select').removeClass('expanded');
                  $self.find('li:gt(0)').each(function() {
                      $(this).addClass('hide');
                  });
              }

              $('body').trigger('bodyClear', [cb]);

          });

          $('select.select').each(function() {

              var $self = $(this),
                  html = [];

              $self.find('option').each(function(index) {
                  var $option = $(this);
                  if ( index < 1 ) {
                      html.push('<li class="rounded-all-inputs value:'+$option.val()+'">'+$option.text()+'</li>');
                  } else {
                      html.push('<li class="rounded-all-inputs hide value:'+$option.val()+'">'+$option.text()+'</li>');
                  }
              });

              $self.after('<div class="custom-select-container" style="height: '+($self.height()+18)+'px;"><ul class="custom-select dropshadow-input rounded-all-inputs">'+html.join('')+'</ul></div>')

          });
      },

      bodyClear: function() {

          $('body').bind('bodyClear', function(e, cb) {

              $('body').bind('click.bodyClear', function() {

                  if ( typeof(cb) === 'function' ) {
                      cb();
                  }

              });

          });

          //$('body').unbind('bodyClear');

      },

      clearStatus: function() {
          $('.mod-status-message').live('hover', function() {
              $(this).attr('title', 'Double-click to clear');
          });
          $('.mod-status-message').live('dblclick', function() {
              $(this).removeClass('~hide').animate({
                  opacity: 'hide',
                  height: ['hide', 'swing']
              }, 500, function() {
                  $(this).addClass('hide');
              });
          });
      },

      highlightFieldNote: function() {
          $('.field-input button, .field-input input, .field-input textarea, .field-input select').bind('mouseover mouseout focus blur', function(e) {

              var $self = $(this);

              if ( e.type === 'focus' || e.type === 'mouseover' ) {
                  $self.parent().next().filter('.field-note').css({
                      color: '#000'
                  });
              } else if (e.type === 'blur' || e.type === 'mouseout' ) {
                  $self.parent().next().filter('.field-note').css({
                      color: '#888'
                  });
              }

          });
      },

      disableAnchor: function() {
          $('.disabled-anchor').removeClass('colorbox').bind('click', function(e) {

              e.preventDefault();
              e.stopPropagation();

          });
      },

      hideModalFormControls: function() {
          $('#cboxClose').live('click.hideModalFormControls', function(e) {
              $('#colorbox .mod-modal-controls').delay(500).queue(function() {
                  $(this).addClass('hide');
                  $(this).dequeue();
              });
          });
      },

      modalAccessibilityLinks: function() {
          $('.mod-modal-header .accessibility a').bind('click', function(e) {
              var $self = $(this);

              $self.prop('target', '_blank');
          });
      },

      revealMembershipDetails: function() {

          $('.mod-membership a, .mod-membership').hover(function(e) {

              var $self = $(this),
                  $details = $self.parent().find('.member-type-details');

              /* PLOUDSRV-182: Why did Aaron just return here if $(this) has
               | the CSS class .mod-membership?  Not sure, but commenting this
               | out resolves PLOUDSRV-182.
               |
               |  if ( $self.hasClass('mod-membership') ) {
               |      return false;
               |  }
               */

              var t = setTimeout(function() {
                  $details.animate({
                      height: 'show',
                      opacity: 'show'
                  }, 300);
              }, 500);

              $self.data('timeout', t);

          }, function(e) {

              var $self = $(this),
                  $details = $self.find('.member-type-details');

              clearTimeout($(this).data('timeout'));

              if ( $self.hasClass('mod-membership') ) {

                  $details.animate({
                      height: 'hide',
                      opacity: 'hide'
                  }, 500);

              }

          });

      },

      init: function() {
          this.bodyClear();
          this.disableAnchor();
          this.setUpColorbox();
          this.kbdOnButtons();
          this.toggleDashboardActionsMenu();
          this.closeActionMenus();
          this.customSelect();
          this.clearStatus();
          this.highlightFieldNote();
          this.hideModalFormControls();
          this.modalAccessibilityLinks();
          this.revealMembershipDetails();
          this.validationSetup();
      }

  };

  Ploud.init();

})();


/*---------------------------------------------------------------------------*\
 |                                 scrollTo()                                |
\*---------------------------------------------------------------------------*/

function scrollTo(id) {
    var elementToScroll = $.browser.safari ? 'body' : 'html';
    var offset = $(id).offset().top;
    $(elementToScroll).animate({
        scrollTop: offset
    }, 'slow', 'swing');
    return false;
}
