(function () {
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  const csrftoken = getCookie('csrftoken');

  if (window.jQuery) {
    $.ajaxSetup({
      beforeSend: function (xhr, settings) {
        const method = (settings.type || '').toUpperCase();
        if (!(/^GET|HEAD|OPTIONS|TRACE$/.test(method))) {
          xhr.setRequestHeader('X-CSRFToken', csrftoken);
        }
      }
    });
  }

  function updateVoteButtons(container, current) {
    const plus = container.find('button[data-value="1"]');
    const minus = container.find('button[data-value="-1"]');

    plus.prop('disabled', current === 1);
    minus.prop('disabled', current === -1);
  }

  $(document).on('click', '.js-q-vote', function () {
    const btn = $(this);
    const id = btn.data('id');
    const value = btn.data('value');
    const container = btn.closest('[data-question-id]');
    const ratingBox = container.find('.js-q-rating');

    $.post('/ajax/question-like/', { id: id, value: value })
      .done(function (data) {
        ratingBox.val(data.rating);
        updateVoteButtons(container, data.current);
      });
  });

  $(document).on('click', '.js-a-vote', function () {
    const btn = $(this);
    const id = btn.data('id');
    const value = btn.data('value');
    const container = btn.closest('[data-answer-id]');
    const ratingBox = container.find('.js-a-rating');

    $.post('/ajax/answer-like/', { id: id, value: value })
      .done(function (data) {
        ratingBox.val(data.rating);
        updateVoteButtons(container, data.current);
      });
  });

  $(document).on('change', '.js-correct-toggle', function () {
    const cb = $(this);
    const qid = cb.data('question-id');
    const aid = cb.data('answer-id');

    $.post('/ajax/mark-correct/', { question_id: qid, answer_id: aid })
      .done(function (data) {
        $('.js-correct-toggle[data-question-id="' + qid + '"]').prop('checked', false);
        if (data.correct_answer_id && data.correct_answer_id !== 0) {
          $('.js-correct-toggle[data-answer-id="' + data.correct_answer_id + '"]').prop('checked', true);
        }
      })
      .fail(function () {
        cb.prop('checked', !cb.prop('checked'));
      });
  });
})();
