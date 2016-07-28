$(function(){

    // #######################
    // ###   Animal App    ###
    // #######################

    // ### spay_neuter field ###
    // Check if spay_neuter is enabled or not to enable spay_neuter_date field
    var $id_spay_neuter_0 = $("#id_spay_neuter_0");
    var $id_spay_neuter_1 = $("#id_spay_neuter_1");
    var $id_spay_neuter_date = $("#id_spay_neuter_date");

    // Hide when load the page
    if (id_spay_neuter_0.checked == false && id_spay_neuter_1.checked == false){
      $id_spay_neuter_date.parents('.control-group').hide();
    }

    // Hide or show on click
    $id_spay_neuter_0.click(function () {
      $id_spay_neuter_date.parents('.control-group').hide();
    });
    $id_spay_neuter_1.click(function () {
      $id_spay_neuter_date.parents('.control-group').show();
    });

    // When editing an animal, check if spay_neuter is "No" to hide spay_neuter_date field.
    if (id_spay_neuter_0.checked){
      $id_spay_neuter_date.parents('.control-group').hide();
    }
});

function ajax_filter_specie_breed(specie_id)
{
   $("#id_breed").html('<option value="">Carregando...</option>');
   $("#id_color").html('<option value="">Carregando...</option>');
   $.ajax({
       type: "GET",
       url: "/animal/select_specie",
       dataType: "json",
       data: {'specie':specie_id},
       success: function(retorno) {
           $("#id_breed").empty();
           $("#id_color").empty();
           $("#id_breed").append('<option value="">--------</option>');
           $("#id_color").append('<option value="">--------</option>');
           $.each(retorno[0], function(i, item){
               $("#id_breed").append('<option value="'+item.pk+'">'+item.valor+'</option>');
           });
           $.each(retorno[1], function(i, item){
               $("#id_color").append('<option value="'+item.pk+'">'+item.valor+'</option>');
           });
       },
       error: function(erro) {
           alert('Erro: Sem retorno de requisição.');
       }
   });
}