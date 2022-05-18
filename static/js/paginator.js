$(function () {
    $('#paginator').DataTable({
      paging: true,
      lengthChange: false,
      searching: false,
      ordering: true,
      info: true,
      autoWidth: false,
      responsive: true,

      "language": {
            "sProcessing":    "Processando...",
            "sLengthMenu":    "Mostrar _MENU_ registros",
            "sZeroRecords":   "Não encontrou resultados",
            "sEmptyTable":    "Ningún dato disponible en esta tabla",
            "sInfo":          "Mostrando registro de _START_ até _END_ de um total de _TOTAL_ registros",
            "sInfoEmpty":     "Mostrando registros de 0 até 0 de um total de 0 registros",
            "sInfoFiltered":  "(filtrado de un total de _MAX_ registros)",
            "sInfoPostFix":   "",
            "sSearch":        "Buscar:",
            "sUrl":           "",
            "sInfoThousands":  ",",
            "sLoadingRecords": "Carregando...",
            "oPaginate": {
                "sFirst":    "Primero",
                "sLast":    "Último",
                "sNext":    "Seguinte",
                "sPrevious": "Anterior"
            },
            "oAria": {
                "sSortAscending":  ": Ativar para ordenar a coluna de maneira ascendente",
                "sSortDescending": ": Ativar para ordenar a coluna de maneira descendente"
            }
        }        
    });

    $('#paginator2').DataTable({
      paging: true,
      lengthChange: true,
      searching: true,
      ordering: true,
      info: true,
      autoWidth: false,
      responsive: true,

      "language": {
            "sProcessing":    "Processando...",
            "sLengthMenu":    "Mostrar _MENU_ registros",
            "sZeroRecords":   "Não encontrou resultados",
            "sEmptyTable":    "Ningún dato disponible en esta tabla",
            "sInfo":          "Mostrando registro de _START_ até _END_ de um total de _TOTAL_ registros",
            "sInfoEmpty":     "Mostrando registros de 0 até 0 de um total de 0 registros",
            "sInfoFiltered":  "(filtrado de un total de _MAX_ registros)",
            "sInfoPostFix":   "",
            "sSearch":        "Buscar:",
            "sUrl":           "",
            "sInfoThousands":  ",",
            "sLoadingRecords": "Carregando...",
            "oPaginate": {
                "sFirst":    "Primero",
                "sLast":    "Último",
                "sNext":    "Seguinte",
                "sPrevious": "Anterior"
            },
            "oAria": {
                "sSortAscending":  ": Ativar para ordenar a coluna de maneira ascendente",
                "sSortDescending": ": Ativar para ordenar a coluna de maneira descendente"
            }
        }        
    });
  });