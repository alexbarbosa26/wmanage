$(document).ready(function () {

    var filterBtn = $('#filter-btn');
    var filterForm = $('#filter-form');

    $(filterBtn).on('click', function () {
        filterForm.submit();
    });

    jQuery('form').preventDoubleSubmit();

    $('[data-toggle="tooltip"]').tooltip({ boundary: 'window', delay: { "show": 500, "hide": 100 } })

    // Captura o evento de seleção da categoria
    $('select[name="categoria"]').change(function() {
        var categoria_id = $(this).val();
        console.log(categoria_id)
        // Faz a requisição AJAX para buscar as subcategorias correspondentes
        $.ajax({
            url: 'subcategorias/',
            data: {
                'categoria_id': categoria_id
            },
            success: function(data) {
                // Limpa as opções atuais do select de subcategorias
                $('select[name="subcategoria"]').empty();
                // Adiciona as novas opções retornadas
                $.each(data, function(index, subcategoria) {
                    $('select[name="subcategoria"]').append($('<option></option>').attr('value', subcategoria.id).text(subcategoria.nome));
                });
            },
            error: function() {
                // Lida com erros de requisição
                alert('Erro ao buscar subcategorias.');
            }
        });
    });
    
});