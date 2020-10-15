UserLogin.controller("ElectricityController", function ($scope) {
    $scope.electricity =
        [
            { month: "01/2010",  units: 291.23, max_units: 400, rooms: 4, cost: 400, predicted_units: 397.32, predicted_cost: 800 },
            { month: "02/2010",  units: 291.23, max_units: 400, rooms: 4, cost: 400, predicted_units: 397.32, predicted_cost: 800 },
            { month: "03/2010",  units: 291.23, max_units: 400, rooms: 4, cost: 400, predicted_units: 397.32, predicted_cost: 800 },
            { month: "04/2010",  units: 291.23, max_units: 400, rooms: 4, cost: 400, predicted_units: 397.32, predicted_cost: 800 },
            { month: "05/2010",  units: 291.23, max_units: 400, rooms: 4, cost: 400, predicted_units: 397.32, predicted_cost: 800 },
            { month: "06/2010",  units: 291.23, max_units: 400, rooms: 4, cost: 400, predicted_units: 397.32, predicted_cost: 800 },
            { month: "07/2010",  units: 291.23, max_units: 400, rooms: 4, cost: 400, predicted_units: 397.32, predicted_cost: 800 },
            { month: "08/2010",  units: 291.23, max_units: 400, rooms: 4, cost: 400, predicted_units: 397.32, predicted_cost: 800 },
        ]

    $scope.getDateElectricity = function getDateElectricity() {

        $('#date_modal').modal({
            backdrop: 'static',
            keyboard: false
        })
        $scope.date_electricity =
            [
                { date: "01/01/2010", kwh: 50, units: 11, max_units: 20 },
                { date: "02/01/2010", kwh: 50, units: 11, max_units: 20 },
                { date: "03/01/2010", kwh: 50, units: 11, max_units: 20 },
                { date: "04/01/2010", kwh: 50, units: 11, max_units: 20 },
                { date: "05/01/2010", kwh: 50, units: 11, max_units: 20 },
                { date: "06/01/2010", kwh: 50, units: 11, max_units: 20 },
                { date: "07/01/2010", kwh: 50, units: 11, max_units: 20 },
                { date: "08/01/2010", kwh: 50, units: 11, max_units: 20 },
                { date: "09/01/2010", kwh: 50, units: 11, max_units: 20 },
                { date: "10/01/2010", kwh: 50, units: 11, max_units: 20 },
            ]
    }

    $scope.getRoomWiseData = function getRoomWiseData() {

        $('#room_modal').modal({
            backdrop: 'static',
            keyboard: false
        })
        // $scope.room_electricity =
        //     [
        //         { name: "BedRoom1", current_units: 131, predicted_units: 143, max_pred_units: 150 },
        //         { name: "BedRoom2", current_units: 85, predicted_units: 102, max_pred_units: 110 },
        //         { name: "Hall", current_units: 164, predicted_units: 188, max_pred_units: 190 },
        //         { name: "Kitchen", current_units: 43, predicted_units: 62, max_pred_units: 70 },
        //         { name: "Misc", current_units: 107, predicted_units: 116, max_pred_units: 120 },
        //     ]
    }        
});




