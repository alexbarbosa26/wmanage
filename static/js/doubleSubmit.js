jQuery.fn.preventDoubleSubmit = function() {
    jQuery(this).submit(function() {
      if (this.beenSubmitted)
        return false;
      else
        this.beenSubmitted = true;
    });
  };