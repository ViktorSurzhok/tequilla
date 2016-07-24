$(document).ready(function () {
        var $image = $('#image');
        var $dataX = $('#dataX');
        var $dataY = $('#dataY');
        var $dataHeight = $('#dataHeight');
        var $dataWidth = $('#dataWidth');
        var $dataRotate = $('#dataRotate');
        var $dataScaleX = $('#dataScaleX');
        var $dataScaleY = $('#dataScaleY');
        var options = {
            //scalable: false,
            zoomable: false,
            zoomOnWheel: false,
            //cropBoxResizable: false,
            aspectRatio: 1,
            crop: function (e) {
                $dataX.val(Math.round(e.x));
                $dataY.val(Math.round(e.y));
                $dataHeight.val(Math.round(e.height));
                $dataWidth.val(Math.round(e.width));
                $dataRotate.val(e.rotate);
                $dataScaleX.val(e.scaleX);
                $dataScaleY.val(e.scaleY);
            }
        };


        // Cropper
        $image.on({
            'build.cropper': function (e) {
                console.log(e.type);
            },
            'built.cropper': function (e) {
                console.log(e.type);
            }

        }).cropper(options);

        $('#super-button').on('click', function () {
            var img = $image.cropper('getCroppedCanvas', {width: 200, height: 200});
            var formData = new FormData();
            formData.append('croppedImage', img.toDataURL());

            $.ajax('/profile/upload_avatar/', {
                    method: "POST",
                    data: formData,
                    processData: false,
                    contentType: false,
                    success: function () {
                         new PNotify({
                                title: 'Ура!',
                                text: 'Новый аватар успешно загружен',
                                type: 'success',
                                styling: 'bootstrap3'
                            });
                         $('.ui-pnotify').fadeIn('slow');
                            setTimeout(function () {
                                $('.ui-pnotify').fadeOut('fast');
                         }, 2000);
                    },
                    error: function () {
                         new PNotify({
                                title: 'Ура!',
                                text: 'Произошла ошибка при загрузке нового аватара.',
                                type: 'success',
                                styling: 'bootstrap3'
                            });
                        $('.ui-pnotify').fadeIn('slow');
                            setTimeout(function () {
                                $('.ui-pnotify').fadeOut('fast');
                        }, 2000);
                    }
                });
        });
});